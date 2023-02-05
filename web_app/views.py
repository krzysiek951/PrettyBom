import logging
import os

from flask import session, render_template, flash, request, redirect, url_for, send_from_directory, current_app, \
    Blueprint
from flask_mail import Message, Mail
from werkzeug.utils import secure_filename

from .exceptions import DelimiterNotUnique, AttrNotSetException, QuantityColumnIsNotDigit
from .models import DefaultBomManager, BomXlsxExporter, PartListCsvImporter, BomProcessor
from .models.processor_director import FullFeatureProcessorDirector
from .typing import *

bp = Blueprint('views', __name__)


def is_allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def required(field, message):
    if not field:
        flash(message)
    return field


@bp.route('/', methods=['GET', 'POST'])
def home_page():
    if request.method == 'POST':
        """
        check if the post request has the file part
        """
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        """
        If the user does not select a file, the browser submits an
        empty file without a filename.
        """
        logging.warning('HOME PAGE DETECTED!')

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and is_allowed_file(file.filename):
            filename = secure_filename(file.filename)
            imported_bom_path_name = os.path.join(current_app.config['IMPORTS_FOLDER'], filename)
            os.makedirs(current_app.config['IMPORTS_FOLDER'], exist_ok=True)
            file.save(imported_bom_path_name)

            imported_bom_header_position: HeaderPositions = request.form['HEADER_POSITION']
            bom_importer = PartListCsvImporter(imported_bom_path_name, imported_bom_header_position)
            user_bom_manager = DefaultBomManager()
            user_bom = user_bom_manager.create_bom()
            bom_importer.import_to(user_bom)

            session['user_bom'] = user_bom
            return redirect(url_for('views.user_data'))

        else:
            flash('Invalid file type. Bill of materials should have a csv extension.')
            return redirect(request.url)

    return render_template('index.html')


@bp.route('/user_data', methods=['GET', 'POST'])
def user_data():
    user_bom = session.get('user_bom')

    if request.method == 'POST':
        bom_attributes = {
            'main_assembly_name': required(request.form['MAIN_ASSEMBLY_NAME'],
                                           'Please provide main assembly full name.'),
            'main_assembly_sets': required(request.form['MAIN_ASSEMBLY_SETS'], 'Please provide main assembly sets.'),
        }

        for key, value in bom_attributes.items():
            setattr(user_bom, key, value)

        processor_attributes = {
            'production_part_keywords': request.form['PRODUCTION_PART_KEYWORDS'],
            'part_position_column': required(request.form['PART_POSITION_COLUMN'],
                                             'Please select part position column.'),
            'part_quantity_column': required(request.form['PART_QUANTITY_COLUMN'],
                                             'Please select part quantity column.'),
            'part_number_column': required(request.form['PART_NUMBER_COLUMN'], 'Please select part number column.'),
            'part_name_column': required(request.form['PART_NAME_COLUMN'], 'Please select part number column.'),
            'junk_part_empty_fields': request.form.getlist('JUNK_PART_EMPTY_FIELDS'),
            'junk_part_keywords': request.form['JUNK_PART_KEYWORDS'],
            'normalized_columns': request.form.getlist('NORMALIZED_COLUMN'),
        }

        bom_processor = BomProcessor(user_bom)
        processor_director = FullFeatureProcessorDirector(bom_processor)
        bom_processor.set_attributes_from_kwargs(**processor_attributes)
        try:
            processor_director.run_processing()

        except DelimiterNotUnique as e:
            part_number = bom_processor.bom_modifiers.get_part_number(e.part)
            part_name = bom_processor.bom_modifiers.get_part_name(e.part)
            flash(f'Only one delimiter of the "Part position" is allowed. '
                  f'Found not unique delimiter: "{e.delimiter}" while checking the following part: '
                  f'{part_number} {part_name}.')

        except AttrNotSetException as e:
            flash(f'The name of the {e.attr_name} must be set.')

        except QuantityColumnIsNotDigit:
            flash('Unable to process the Part list - Quantity column contains values other than numbers.')

        if '_flashes' in session:
            return redirect(request.url)

        exported_columns = required(request.form.getlist('EXPORT_COLUMNS'),
                                    'Please select at least one column to export.')
        os.makedirs(current_app.config['EXPORTS_FOLDER'], exist_ok=True)
        bom_exporter = BomXlsxExporter(user_bom)
        bom_exporter.export_part_list(exported_columns, current_app.config['EXPORTS_FOLDER'])
        bom_processor.undo_processing()
        session['exported_filename'] = bom_exporter.exported_filename

        return redirect(url_for('views.download'))

    export_available_columns = user_bom.imported_bom_columns + current_app.config['PART_ADDITIONAL_FIELDS']
    return render_template('user_data.html', imported_bom_columns=user_bom.imported_bom_columns,
                           export_available_columns=export_available_columns)


@bp.route('/download', defaults={'url_filename': None}, methods=['GET', 'POST'])
@bp.route('/download/<path:url_filename>', methods=['GET', 'POST'])
def download(url_filename):
    exported_filename = session.get('exported_filename')

    if url_filename:
        exported_bom_directory = os.path.join(os.getcwd(), current_app.config['EXPORTS_FOLDER'])
        return send_from_directory(exported_bom_directory, url_filename, as_attachment=True)
    return render_template('download.html', exported_file_path=exported_filename)


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    mail = Mail()
    mail.init_app(current_app)
    if request.method == 'POST':
        msg = Message()
        msg.subject = request.form['subject']
        msg.recipients = ["krzysiek951@gmail.com"]
        msg.reply_to = request.form['email']
        msg.html = f"New email from {request.form['name']}: {request.form['email']}:<br><br>{request.form['message']}"
        mail.send(msg)
        flash('Thank You! Your email was sent successfully!')

    return render_template('contact.html')
