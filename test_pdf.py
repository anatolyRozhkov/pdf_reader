from pdf_to_dict import ValidatePDF

# you can use this sample to play around with tests
bad_sample = {'name': 'some name', 'long barcode':  '111', 'PN': 'tst', 'SN': '123123', 'DESCRIPTION': 'PART', 'LOCATION': '111', 'CONDITION': 'FN', 'RECEIVER#': '9', 'UOM': 'EA', 'EXP DATE': '13.04.2022', 'PO': 'P101', 'CERT SOURCE': 'wef', 'REC.DATE': '18.04.2022', 'MFG': 'efwfe', 'BATCH#': '1', 'DOM': '04.04.2022', 'REMARK': None, 'LOT#': '1', 'TAGGED BY': '1', 'Qty': '1', 'NOTES': 'inspection notes'}


def test_pdf_fields(app_config):
    """
    This test knows that:

    pdf should be presented as a dict containing strs, ints, dates or a None
    it knows of what type() each value should be.

    If a 'required field' contains None or the 'field'
    contains incorrect type()/corrupted data,
    it will through a ValueError with a debug message.

    WARNING:
        if you strike out some lines in a tool like IlovePDF,
        it is likely that pdf_to_dict will still be able to read
        under edits and pass.
    """

    days_in_each_month = {
        '01': 31, '02': 28, '03': 31, '04': 30, '05': 31, '06': 30, '07': 31, '08': 31, '09': 30, '10': 31, '11': 30, '12': 31
    }

    # contains expected formats for each key
    type_dict = {
            'name': str, 'long barcode': str, 'PN': str, 'SN': int, 'DESCRIPTION': str, 'LOCATION': int,
            'CONDITION': str, 'RECEIVER#': int, 'UOM': str, 'EXP DATE': 'date', 'PO': str,
            'CERT SOURCE': str, 'REC.DATE': 'date', 'MFG': str, 'BATCH#': int, 'DOM': 'date',
            'REMARK': None, 'LOT#': int, 'TAGGED BY': int, 'Qty': int, 'NOTES': str
        }

    # you can pass bad sample here to play around with this test
    pdf = ValidatePDF(app_config.pdf)
    result_dict = pdf.result_dict

    for key, value in type_dict.items():

        # test string fields
        if value == str:
            try:
                assert type(result_dict[key]) is str
            except AssertionError:
                raise ValueError(f'value "{result_dict[key]}" supposed to be a str, but it is {type(result_dict[key])}')

        # test integer fields
        elif value == int:
            try:
                value(result_dict[key])
            except (ValueError, TypeError) as e:
                raise ValueError(f'value "{result_dict[key]}" supposed to be an int, but it is {type(result_dict[key])}')

        # test if date is date at all
        elif value == 'date':
            try:
                string_of_int = result_dict[key].replace('.', '')
                int(string_of_int)
            except (ValueError, TypeError) as e:
                raise ValueError(f'value "{result_dict[key]}" is supposed to be a date, but it is {type(result_dict[key])}')

            # test if date has correct format
            string_of_int = result_dict[key].replace('.', '')
            int(string_of_int)
            if len(string_of_int) == 8:
                pass
            else:
                raise ValueError(f'date {result_dict[key]} has an incorrect format, the format should be like this: dd.mm.yyyy')

            # test days and months
            dd_mm_yy_list = result_dict[key].split('.')
            month = dd_mm_yy_list[1]
            day = dd_mm_yy_list[0]

            # test if month is valid
            try:
                assert int(month) <= 12
            except AssertionError:
                raise ValueError(f'date: "{result_dict[key]}" contains month that does not exist')

            # test if number of days is ok for that month
            try:
                assert int(day) <= days_in_each_month[month]
            except AssertionError:
                raise ValueError(f'date: "{result_dict[key]}" has an incorrect number of days for that month, must be: "{days_in_each_month[month]}"')


def test_pdf_structure(app_config):
    """
    This test knows that PDF should be presented as a list
    each value of the list corresponds to a line. It expects other
    PDF to have the same line structure.

    If a line doesn't have expected fields,
    it will through a ValueError with a debug message.
    """

    structure_dict = {
        0: [''], 1: ['PN', 'SN'], 2: ['DESCRIPTION'],
        3: ['LOCATION', 'CONDITION:'], 4: ['RECEIVER#', 'UOM'],
        5: ['EXP DATE', 'PO'], 6: ['CERT SOURCE'], 7: ['REC.DATE', 'MFG'],
        8: ['BATCH#', 'DOM'], 9: ['REMARK'], 10: ['TAGGED BY'], 11: [''],
        12: ['Qty', 'NOTES'], 13: ['']
    }

    # load pdf as a list of lines
    pdf = ValidatePDF(app_config.pdf)
    list_of_lines = pdf.list_of_lines()

    for index in range(len(list_of_lines)):

        if len(list_of_lines) > len(structure_dict):
            raise ValueError('PDF has an invalid structure, the number of lines is greater than expected')

        # test if lines contain expected fields
        for value in structure_dict[index]:
            if value in list_of_lines[index]:
                assert True
            else:
                raise ValueError('PDF has invalid structure')
