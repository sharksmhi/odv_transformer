from ctdpy.core.session import Session
from ctdpy.core.utils import generate_filepaths
import time
from pprint import pprint
import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    # GET FILES
    # base_dir = '...\\Svea_v16 april\\CTD\\data'  # tar längre tid att läsa ifrån filtjänst
    base_dir = r'ctdpy\ctdpy\tests\test_data\exprapp_april_2020'
    #base_dir = r"\\winfs-proj\proj\havgem\EXPRAPP\Exprap2022\Svea_v40-41_BIAS_oktober\CTD\CNV" 
    base_dir = r"\\winfs-proj\proj\havgem\LenaV\temp\umsc_subset_2021"

    """    ## if not xlsx metadatafile with delivery
    files = generate_filepaths(
        base_dir,
        # pattern_list=['.cnv', '.xlsx'],  # Both cnv- and metadata-files
        endswith='.cnv',  # Only cnv-files
        # endswith='.txt',  # Presumably CTD-standard format
        only_from_dir=True,  # we exclude search of files from folders under "base_dir"
    )
    # Create SESSION object
    s = Session(
        filepaths=files,
        reader='smhi',
    )
    # READ DELIVERY DATA, CNV, XLSX
    start_time = time.time()
    datasets = s.read()
    print("Datasets loaded--%.3f sec" % (time.time() - start_time))
    print('Files loaded:')
    pprint(list(datasets[0].keys()))
    # WRITE METADATA TO TEMPLATE
    # datasets are stored in a list of 2 (idx 0: data, idx 1: metadata). For this example we only have data
    s.save_data(
            datasets[0],
            save_path = f"{base_dir}/",
            writer='metadata_template',
        )

    print("Metadata file created--%.3f sec" % (time.time() - start_time))
    exit()
    """

    ### Create internal format for archiving ###

    files = generate_filepaths(
    base_dir,
    pattern_list=['.cnv', '.xlsx'],  # Both cnv- and metadata-files
    only_from_dir=False,
    )
    # Create SESSION object
    start_time = time.time()
    s = Session(
        filepaths=files,
        reader='umsc',
    )
    print("Session--%.3f sec" % (time.time() - start_time))

    # READ DELIVERY DATA, CNV, XLSX
    start_time = time.time()
    datasets = s.read()
    print("Datasets loaded--%.3f sec" % (time.time() - start_time))
    print('Files loaded:')
    pprint(list(datasets[0].keys()))
    pprint(list(datasets[1].keys()))

    # SAVE DATA ACCORDING TO CTD STANDARD FORMAT (TXT)
    data_path = s.save_data(
        datasets,
        save_path = base_dir,
        writer='ctd_standard_template',
        return_data_path=True,
    )
