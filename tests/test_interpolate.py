from beancount import loader
from beancount.parser import printer
from beancount.core.compare import compare_entries

from context import interpolate

def test_plugin():
    
    infile_entries, infile_errors, _ = loader.load_file("test_input.beancount")
    assert not infile_errors

    outfile_entries, outfile_errors, _ = loader.load_file("test_output.beancount")
    assert not outfile_errors

    test_entries, test_errors, _ = interpolate.interpolate(infile_entries, [], {})
    assert len(test_errors) == 3

    success, missing, wrong = compare_entries(outfile_entries, test_entries)

    print("Entries Missing from Test Output:", len(missing))
    printer.print_entries(missing)

    print("Inapropriate Entries in Test Output:", len(wrong))
    #printer.print_entries(wrong)

    print("Total Entries in Test Output:", len(outfile_entries))
    assert success
        
