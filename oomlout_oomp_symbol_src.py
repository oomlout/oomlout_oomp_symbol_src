import os
import yaml

from kiutils.symbol import SymbolLib

empty_library_file = 'templates/empty.kicad_sym'

def clone_and_copy_symbols():
    #load repos from repos.yaml and repos_manual.yaml
    repos = []
    with open('repos.yaml', 'r') as f:
        new = yaml.load(f, Loader=yaml.FullLoader)
        if new != None:
            repos += new
    with open('repos_manual.yaml', 'r') as f:
        new = yaml.load(f, Loader=yaml.FullLoader)
        if new != None:
            repos += new

    kicad_syms = load_symbols_from_files(repos=repos)    
    #copy_symbol_libraries_to_new_directories(kicad_syms=kicad_syms)

    # start to do more major things
    symbols_all = get_all_symbols_from_kicad_syms(kicad_syms=kicad_syms)
    make_mega_library(symbols_all=symbols_all)
    make_a_flat_representation_with_one_simple_per_directory(symbols_all=symbols_all)


def load_symbols_from_files(**kwargs):
    print("Cloning repos and loading kicad_syms from files")
    kicad_syms = []
    repos = kwargs['repos']
    #clone repos
    for repo in repos:
        owner = repo['owner']
        name = repo['name']
        #print what you're doing
        print('Cloning {} from {}'.format(name, owner))
        #clone the repo into tmp/
        os.system(f'git clone {repo["url"]} tmp/{name}')
        #get a list of all the files that end in kicad_sym
        
        for root, dirs, files in os.walk(f'tmp/{name}'):
            for file in files:
                if file.endswith('kicad_sym'):
                    #skip all ones with fpga in the name to save space
                    if 'fpga' not in file.lower():
                        deets = {}
                        kicad_sym = os.path.join(root, file)
                        #replace \\ with / for windows
                        kicad_sym = kicad_sym.replace('\\', '/')
                        deets['kicad_sym'] = kicad_sym
                        deets['repo'] = repo
                        kicad_syms.append(deets)
    #copy all the kicad_syms into the oomlout_oomp_symbol_src directory
    #dump kicas_syms to yaml
    return kicad_syms

def copy_symbol_libraries_to_new_directories(**kwargs):
    #just copies files across
    print("Copying symbol libraries to new directories")
    kicad_syms = kwargs['kicad_syms']
    for ks in kicad_syms:
        kicad_sym = ks["kicad_sym"]
        repo = ks["repo"]
        owner = repo["owner"]
        name = repo["name"]
        #copy using shutil
        import shutil

        ###### symbols_folder_library
        src = kicad_sym
        #replace \\ with / for windows
        src = src.replace('\\', '/')
        #remove tmp/
        dst = src
        dst = dst.replace('tmp/', '')
        #add owner
        dst = f'{owner}/{dst}'
        dst = f'symbols_folder_library/{dst}'
        #make sure the directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
    
        ###### symbols_flat_library
        src = kicad_sym
        #replace \\ with / for windows
        src = src.replace('\\', '/')
        #remove tmp/
        dst = src            
        dst = dst.replace('tmp/', '')
        dst = dst.replace('/', '_')
        dst = f'{owner}_{dst}'
        dst = f'symbols_flat_library/{dst}'
        #make sure the directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        print('.', end='')
    print()
    print("Done copying symbol libraries to new directories")

def get_all_symbols_from_kicad_syms(**kwargs):
    
    print("Loading symbols from kicad_syms")
    kicad_syms = kwargs['kicad_syms']
    symbols = []
    #clip kicad_syms for testing
    #kicad_syms = kicad_syms[:10]
    for ks in kicad_syms:
        
        kicad_sym = ks["kicad_sym"]
        print(f"loading symbol from {kicad_sym}")
        repo = ks["repo"]
        owner = repo["owner"]
        
        #load the symbol
        try:
            sym = SymbolLib().from_file(kicad_sym)
            if sym != None:
                #libaryr name is just the filename of kicad_sym
                library_name = kicad_sym.replace('.kicad_sym', '').replace('tmp/', '')
                #replace / with _
                library_name = library_name.replace('/', '_')
                library_name = library_name.replace('-', '_')
                #add owner and name to each symbol
                for symbol in sym.symbols:                        
                    entry_name_original = symbol.entryName
                    entry_name = f'{owner}_{library_name}_{symbol.entryName}'

                    symbol.entryName = symbol.entryName.replace(entry_name_original, entry_name)
                    for unit in symbol.units:
                        unit.entryName = unit.entryName.replace(entry_name_original, entry_name)
                    #if extends
                    if symbol.extends != None:
                        extend_extra = f'{owner}_{library_name}'
                        symbol.extends = f'{extend_extra}_{symbol.extends}'
                    deets = {}
                    deets['symbol'] = symbol
                    deets['repo'] = repo
                    deets["library_name"] = library_name
                    symbols.append(deets)                    
        except Exception as e:
            print(f'Failed to load {kicad_sym}')
            print(e)
        print(f'Loaded {kicad_sym}')
        #dump symbols to yaml
    return symbols

def make_mega_library(**kwargs):
    symbols_all = kwargs['symbols_all']
    
    #make a mega symbol library
    print("Making a mega symbol library")
    
    counter = 0
    counter_file = 0
    symbols_per = 2500
    test_string_last = ""
    can_split = False
    from kiutils.symbol import SymbolLib
    sym = SymbolLib().from_file(empty_library_file)
    ######## splitting isn't working need to split so a library is all in the same file
    for symb in symbols_all:
        symbol = symb['symbol']
        repo = symb['repo']
        name = repo['name']
        owner = repo['owner']
        remove_string = f'{owner}_{name}_'
        #replace / with _
        remove_string = remove_string.replace('/', '_')
        remove_string = remove_string.replace('-', '_')

        
        
        #test string equals all charachters up to the second underscore
        
        
        entry_name_usable = symbol.entryName.replace(remove_string, '')
        test_string_current = entry_name_usable.split('_')[0] + '_' + entry_name_usable.split('_')[1]
        #if test string last is empty, set it to test string current

        #initialization
        if test_string_last == "":
            test_string_last = test_string_current
        
        #if test string current doesn't equals test string last, can split
        if test_string_current != test_string_last:
            if counter >= symbols_per:
                #extra check because was making a mistake with diodes
                if 'diode' not in test_string_current.lower():
                    library_file = f'symbols_all_the_symbols_one_library/all_the_symbols_one_library_{counter_file}.kicad_sym'
                    #create directories if needed
                    os.makedirs(os.path.dirname(library_file), exist_ok=True)
                    print(f'Writing {library_file}')
                    sym.to_file(library_file)
                    print(f'Wrote {library_file}')
                    sym = SymbolLib().from_file(empty_library_file)
                    counter = 0
                    counter_file += 1
        
        sym.symbols.append(symbol)

        #print a dot every 1000 symbols
        if counter % 400 == 0:
            print('.', end='', flush=True)
        counter += 1
        
        test_string_last = test_string_current

    library_file = f'symbols_all_the_symbols_one_library/all_the_symbols_one_library_{counter_file}.kicad_sym'
    #create directories if needed
    os.makedirs(os.path.dirname(library_file), exist_ok=True)
    sym.to_file(library_file)
    return symbols_all

def make_a_flat_representation_with_one_simple_per_directory(**kwargs):
    print("Making a flat representation with one symbol per directory")
    symbols_all = kwargs['symbols_all']
    #make a flat representation
    print("Making a flat representation")
    count = 0
    for symb in symbols_all:
        symbol = symb['symbol']
        current_owner = symb['repo']['owner']
        current_entry_name = symbol.entryName.replace(f'{current_owner}_', '')
        symbol_name = f'{current_owner}_{symb["repo"]["name"]}_{current_entry_name}'
        #replace / with _
        symbol_name = symbol_name.replace('.kicad_mod', '')
        symbol_name = symbol_name.replace('/', '_')
        symbol_name = symbol_name.replace('\\', '_')
        symbol_name = symbol_name.replace(':', '_')
        symbol_name = symbol_name.replace('*', '_')
        symbol_name = symbol_name.replace('?', '_')
        symbol_name = symbol_name.replace('"', '_')
        symbol_name = symbol_name.replace('<', '_')
        symbol_name = symbol_name.replace('>', '_')
        symbol_name = symbol_name.replace('|', '_')
        symbol_name = symbol_name.replace('-', '_')        
        symbol_name = symbol_name.replace('+', '_')
        symbol_name = symbol_name.replace(' ', '_')
        symbol_name = symbol_name.replace('.', '_')
        symbol_name = symbol_name.replace('__', '_')
        symbol_name = symbol_name.replace('__', '_')
        symbol_name = symbol_name.replace('__', '_')
        symbol_name = symbol_name.replace('__', '_')
        directory_name = f'symbols_flat/{symbol_name}/working'
        library_name = f'{directory_name}/working.kicad_sym'
        #skip if extends not in symbol[symbol] or if it doesn't equal none
        if symbol.extends == None:        
            #change entryID
            #load an empty library
            sym = SymbolLib().from_file(empty_library_file)
            #add the symbol to the library
            sym.symbols.append(symbol)
            #create directories if needed
            os.makedirs(os.path.dirname(library_name), exist_ok=True)
            #write the library
            sym.to_file(library_name)
            #print a dot every 100 times through
            count += 1
            if count % 100 == 0:
                print('.', end='')
        else:
            #might just need to include the extension
            entry_name = symbol.entryName
            print(f'Skipping {entry_name} becaue it extends')
    print()