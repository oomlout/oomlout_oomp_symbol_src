import os
import yaml

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
    symbols_all = []
    #clone repos
    for repo in repos:
        owner = repo['owner']
        name = repo['name']
        #print what you're doing
        print('Cloning {} from {}'.format(name, owner))
        #clone the repo into tmp/
        os.system(f'git clone {repo["url"]} tmp/{name}')
        #get a list of all the files that end in kicad_sym
        kicad_syms = []
        for root, dirs, files in os.walk(f'tmp/{name}'):
            for file in files:
                if file.endswith('kicad_sym'):
                    ks = os.path.join(root, file)
                    #replace \\ with / for windows
                    ks = ks.replace('\\', '/')
                    kicad_syms.append(ks)
        #copy all the kicad_syms into the oomlout_oomp_symbol_src directory
        for kicad_sym in kicad_syms:
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
        
        #mega symbol file
        from kiutils.symbol import SymbolLib
        #try to load all symbols in
        symbols = []
        #clipping 
        #kicad_syms = kicad_syms[:2]
        for kicad_sym in kicad_syms:
            try:
                sym = SymbolLib().from_file(kicad_sym)
                if sym != None:
                    #libaryr name is just the filename of kicad_sym
                    library_name = os.path.basename(kicad_sym).replace('.kicad_sym', '')
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
                print(f'Loaded {kicad_sym}')

            except:
                print(f'Could not load {kicad_sym}')
        pass
        symbols_all.extend(symbols)

    #make a mega symbol library
    print("Making a mega symbol library")
    empty_library_file = 'templates/empty.kicad_sym'
    counter = 0
    counter_file = 0
    symbols_per = 5000
    sym = SymbolLib().from_file(empty_library_file)
    for symbol in symbols_all:
        sym.symbols.append(symbol['symbol'])
        counter += 1
        if counter >= symbols_per:                    
            library_file = f'symbols_all_the_symbols_one_library/all_the_symbols_one_library_{counter_file}.kicad_sym'
            #create directories if needed
            os.makedirs(os.path.dirname(library_file), exist_ok=True)
            sym.to_file(library_file)
            print(f'Wrote {library_file}')
            sym = SymbolLib().from_file(empty_library_file)
            counter = 0
            counter_file += 1
    counter_file += 1
    library_file = f'symbols_all_the_symbols_one_library/all_the_symbols_one_library_{counter_file}.kicad_sym'
    #create directories if needed
    os.makedirs(os.path.dirname(library_file), exist_ok=True)
    sym.to_file(library_file)

    #make a flat representation
    print("Making a flat representation")
    count = 0
    for symbol in symbols_all:
        current_owner = symbol['repo']['owner']
        current_entry_name = symbol['symbol'].entryName.replace(f'{current_owner}_', '')
        symbol_name = f'{current_owner}_{symbol["repo"]["name"]}_{current_entry_name}'
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
        if symbol['symbol'].extends == None:        
            #change entryID
            #load an empty library
            sym = SymbolLib().from_file(empty_library_file)
            #add the symbol to the library
            sym.symbols.append(symbol['symbol'])
            #create directories if needed
            os.makedirs(os.path.dirname(library_name), exist_ok=True)
            #write the library
            sym.to_file(library_name)
            #print a dot every 100 times through
            count += 1
            if count % 100 == 0:
                print('.', end='')
        else:
            entry_name = symbol['symbol'].entryName
            print(f'Skipping {entry_name} becaue it extends')
    print()


