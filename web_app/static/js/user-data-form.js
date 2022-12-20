$(function () {

    const sortableInputList = $("#sortable-input-list");
    const sortableOutputList = $("#sortable-output-list");

    const createExportSortableList = (parent, optionsList) => {
        optionsList.forEach(function (option, index) {
            $('<li>', {
                id: 'option-' + index,
                class: 'list-group-item',
                text: option.replace(/\_/g, " "),
            }).appendTo(parent);
        })
    }

    const createOptions = (parent, optionsList, isMultiple) => {
        optionsList.forEach(function (option) {
            $('<option>', {
                text: option,
                value: option,
            }).appendTo(parent);
        });

        if (!isMultiple) {
            $('<option>', {
                text: '--- Select column name ---',
                value: '',
                selected: true,
            }).prependTo(parent);
        }
    }

    const handleSortableListDblClick = function () {
        const listItem = $(this).clone();
        const isInputList = $(this).closest('.connected-sortable')[0] === sortableInputList[0]
        isInputList ? sortableOutputList.append(listItem) : sortableInputList.append(listItem);
        listItem.dblclick(handleSortableListDblClick);
        $(this).remove();
        handleSortableListChange();
    }

    const handleAddRemoveAllSortableItems = function (event) {
        const currentList = event.data.method === 'add' ? sortableInputList : sortableOutputList
        currentList.find('li').each(function () {
            const listItem = $(this).clone();
            event.data.method === 'add' ? sortableOutputList.append(listItem) : sortableInputList.append(listItem);
            listItem.dblclick(handleSortableListDblClick);
            $(this).remove();
        });
        handleSortableListChange();
    }

    const handleSortableListChange = function () {
        $('.sortable-container input').remove();

        const exportOutputList = sortableOutputList.sortable("toArray");

        if (exportOutputList.length) {
            exportOutputList.forEach(function (item) {
                $('<input>', {
                    name: 'EXPORT_COLUMNS',
                    type: 'text',
                    class: 'form-control d-none',
                    required: true,
                    value: exportAvailableColumns[item.split('-')[1]],
                }).insertBefore($('.sortable-container > .row'));
            })
        } else {
            $('<input>', {
                name: 'EXPORT_COLUMNS',
                type: 'text',
                class: 'form-control d-none',
                required: true,
                value: '',
            }).prependTo($('.sortable-container'));
        }
    }

    $("#PART_POSITION_COLUMN, #PART_QUANTITY_COLUMN, #PART_NUMBER_COLUMN, #PART_NAME_COLUMN").each(function (_, element) {
        createOptions(element, importedBomColumns, false);
    })

    $("#NORMALIZED_COLUMN, #JUNK_PART_EMPTY_FIELDS").each(function (_, element) {
        createOptions(element, importedBomColumns, true);
    })

    createExportSortableList(sortableInputList, exportAvailableColumns);

    sortableInputList.add(sortableOutputList).sortable({
        placeholderClass: 'list-group-item',
        connectWith: '.connected-sortable',
    })
    sortableOutputList.on('sortdeactivate', function(_, __){ handleSortableListChange() })

    $('.sortable-container .connected-sortable li').dblclick(handleSortableListDblClick);
    $('#sortable-add-all').click({method: 'add'}, handleAddRemoveAllSortableItems)
    $('#sortable-remove-all').click({method: 'remove'}, handleAddRemoveAllSortableItems)

    $('form').on('submit', function() {
        const invalidFields = $('form.was-validated :invalid');
        if(invalidFields.length){
            $('html, body').animate({scrollTop: invalidFields.first().offset().top - 140 });
        }
        return true;
    });
});
