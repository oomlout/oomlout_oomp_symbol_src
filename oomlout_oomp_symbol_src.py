import os
import yaml
import oom_kiutils
import oom_base

from kiutils.symbol import SymbolLib

empty_library_file = 'templates/empty.kicad_sym'

github_repos = {}

def clone_and_copy_symbols(**kwargs):
    dir_base = kwargs.get('dir_base', 'tmp/data/oomlout_oomp_symbol_src')
    #set cwd
    old_cwd = os.getcwd()
    os.chdir(dir_base)
    test = kwargs.get('test', False)
    #load repos from repos.yaml and repos_manual.yaml
    repos = []
    if not test:
        with open('repos.yaml', 'r') as f:
            new = yaml.load(f, Loader=yaml.FullLoader)
            if new != None:
                repos += new
        with open('repos_manual.yaml', 'r') as f:
            new = yaml.load(f, Loader=yaml.FullLoader)
            if new != None:
                repos += new
    else:
        with open('repos_test.yaml', 'r') as f:
            new = yaml.load(f, Loader=yaml.FullLoader)
            if new != None:
                repos += new
    # add name and owner from repo extract from the url
    for repo in repos:
        url = repo['url']
        #get from repo github address https://github.com/oomlout/oomlout_oomp_part_templates
        #get owner from url
        if "github" in url:
            owner = url.split('/')[-2]
            name = url.split('/')[-1]
        elif "gitlab" in url:
            owner = url.split('/')[-3]
            name = url.split('/')[-1]
        repo['owner'] = owner
        repo['name'] = name
    
    kicad_syms = load_symbols_from_files(repos=repos)    
    copy_symbol_libraries_to_new_directories(kicad_syms=kicad_syms)

    # start to do more major things
    symbols_all = get_all_symbols_from_kicad_syms(kicad_syms=kicad_syms)
    make_mega_library(symbols_all=symbols_all)
    make_a_flat_representation_with_one_simple_per_directory(symbols_all=symbols_all)
    #return cwd to normal
    os.chdir(old_cwd)

def load_symbols_from_files(**kwargs):
    print("Cloning repos and loading kicad_syms from files")
    kicad_syms = []
    repos = kwargs['repos']
    #clone repos
    for repo in repos:
        url = repo['url']
        #get from repo github address https://github.com/oomlout/oomlout_oomp_part_templates
        #get owner from url
        if "github" in url:
            owner = url.split('/')[-2]
            name = url.split('/')[-1]
        elif "gitlab" in url:
            owner = url.split('/')[-3]
            name = url.split('/')[-1]
        #print what you're doing
        import oom_git
        oom_git.clone(repo=url, directory = f'tmp/')
        dir_full = f'tmp/{name}'        
        
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
        url = repo['url']
        name = repo['name']
        owner = repo['owner']
        import shutil
        """
        ###### symbols_folder_library
        src = kicad_sym
        #replace \\ with / for windows
        src = src.replace('\\', '/')
        #remove tmp/
        dst = src
        #remove folders just filename for dst
        dst = dst.split('/')[-1]


        
        #lower case
        dst = dst.lower()
        #add owner
        dst = f'{owner}/{dst}'
        dst = f'symbols_folder_library/{dst}'
        #make sure the directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        """
    """
        ###### symbols_flat_library
        src = kicad_sym
        #replace \\ with / for windows
        src = src.replace('\\', '/')
        #remove tmp/
        dst = src            
        dst = dst.split('/')[-1]
        dst = f'{owner}_{dst}'
        # lower case
        dst = dst.lower()
        dst = f'symbols_flat_library/{dst}'
        #make sure the directory exists
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        print('.', end='')
    print()
    print("Done copying symbol libraries to new directories")
    """

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
        #get reponame from repo
        url = repo['url']
        #get from repo github address https://github.com/oomlout/oomlout_oomp_part_templates
        #get owner from url
        if "github" in url:
            owner = url.split('/')[-2]
            name = url.split('/')[-1]
        elif "gitlab" in url:
            owner = url.split('/')[-3]
            name = url.split('/')[-1]
        repo["github_src"] = f"{url}{kicad_sym.replace('tmp/', '').replace(name, '')}"

        
        
        #loa#d the symbol
        try:
            cwd = os.getcwd()
            sym = SymbolLib().from_file(kicad_sym.replace('/', '\\'))
        
            if sym != None:
                
                #libaryr name is just the filename of kicad_sym
                library_name = kicad_sym.split('/')[-1]
                library_name = library_name.replace('.kicad_sym', '').replace('tmp/', '')
                #replace / with _
                library_name = library_name.replace('/', '_')
                library_name = library_name.replace('-', '_')
                #add owner and name to each symbol
                
                
                for symbol in sym.symbols: 

                    symbol = oom_kiutils.symbol_change_name_oomp(symbol=symbol, library_name=library_name, repo=repo)
                    deets = {}
                    deets['symbol'] = symbol
                    deets['repo'] = repo
                    deets["library_name"] = library_name
                    deets["repo_github"] = get_repo_from_github(repo=repo)
                    #symbol_name = f'{current_owner}_{library_name}_{current_entry_name}'
                    


                    owner = repo['owner']
                    deets["owner"] = owner
                    library = library_name.lower()
                    deets["library"] = library
                    name = symbol.entryName.replace(f'{library}_', '').replace(f'{repo["owner"]}_', '')
                    deets["name"] = name
                    id = f'{owner}_{library}_{name}'
                    deets["id"] = id
                    print(f"loading symbol {id}")

                    if "h4pra" in name:
                        pass

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
    symbols_per = 1500
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
                    #library_file = f'symbols_all_the_symbols_one_library/all_the_symbols_one_library_{counter_file}.kicad_sym'
                    library_file = f"tmp/generated/oomlout_oomp_symbol_all_the_kicad_symbols/all_the_symbols_one_library_{counter_file}.kicad_sym"
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

    library_file = f"tmp/generated/oomlout_oomp_symbol_all_the_kicad_symbols/all_the_symbols_one_library_{counter_file}.kicad_sym"
    #create directories if needed
    cwd = os.getcwd()
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
        #id = symb['repo']['owner']
        id = symb['id']
        

        symbol_name = id
        #replace / with _
        #if "not symbol_name.startswith("arturo182"): 
        if "ina219xidc" in symbol_name:
            pass
        #lower case
        symbol_name = symbol_name.lower()
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
        #create if it doesn't exist
        os.makedirs(os.path.dirname(directory_name), exist_ok=True)

        folder = f'{symbol_name}/working'
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
        
        #add various useful links to footprint details
            links = {}
            repo_full = symb['repo_github']
            if len(repo_full) > 2:
                #get the repo url details from github using their api
                html_url = repo_full['html_url']
                github_src = symb["repo"]["github_src"]
                links['github_src'] = github_src
                links['github_src_repo'] = html_url
                #get owner from html_url
                owner = html_url.split('/')[-2]
                links['github_owner'] = f'{owner}'
                #get repo name from html_url
                repo_name = html_url.split('/')[-1]
                links['github_repo_name'] = f'{repo_name}'
            else:
                ###kicad on gitlab
                html_url = 'https://gitlab.com/kicad/libraries/kicad-symbols'
                github_src = f"{symb['repo']['github_src']}"
                github_src = github_src.replace('github.com', 'gitlab.com')
                links['github_src'] = github_src
                links['github_src_repo'] = html_url
                #get owner from html_url
                ##owner = html_url.split('/')[-2]
                ##links['github_owner'] = f'{owner}'
                #get repo name from html_url
                ##repo_name = html_url.split('/')[-1]
                ##links['github_repo_name'] = f'{repo_name}'
            #oomp_src flat link
            oomp_src_flat = f'symbols_flat/{folder}'
            links['oomp_src_flat'] = oomp_src_flat
            oomp_src_flat_github = f'https://github.com/oomlout/oomlout_oomp_symbol_src/tree/main/{folder}'
            links['oomp_src_flat_github'] = oomp_src_flat_github
            
            
            #oomp_bot link
            oomp_bot_folder = folder.replace("symbols_flat","symbols")
            oomp_bot = f'{oomp_bot_folder}'
            links['oomp_bot'] = oomp_bot
            oomp_bot_github = f'https://github.com/oomlout/oomlout_oomp_symbol_bot/tree/main/{oomp_bot_folder}'
            links['oomp_bot_github'] = oomp_bot_github
            
            #doc folder
            oomp_doc_folder = folder.replace("symbols_flat","symbols")
            oomp_bot = f'{oomp_doc_folder}'
            links['oomp_doc'] = oomp_bot
            oomp_doc_github = f'https://github.com/oomlout/oomlout_oomp_symbol_doc/tree/main/{oomp_bot_folder}'
            links['oomp_doc_github'] = oomp_doc_github

            

            #add links to footprint details
            symb['links'] = links

        
            symb['oomp_key'] = f'oomp_{symbol_name}'
            symb['oomp_key_simple'] = f'{symbol_name}'
            
            
        
        else:
            #might just need to include the extension
            entry_name = symbol.entryName
            print(f'Skipping {entry_name} becaue it extends')

        

        #dump all the details we know to a yaml
        print(f'Writing {directory_name}/working.yaml')
        #create directories if needed
        os.makedirs(os.path.dirname(f'{directory_name}/working.yaml'), exist_ok=True)

        #make a deepcopy of symb
        import copy
        symb2 = copy.deepcopy(symb)
        #remove symbol from symb
        symb2.pop('symbol')

        

        import oom_base

        current_entry_name = symb["name"]
        symbol_name = current_entry_name

        

        owner_name = ""
        repo = symb2.get('repo', "")
        if repo != "":
            owner_name = repo.get('owner', "")
        
        library_name = symb2.get('library_name', "")
        ## remove special characters and lower using oom_base
        library_name = oom_base.remove_special_characters(library_name)
        library_name = library_name.lower()

        #add a md5 hash of the id as a keyed item to kwargs
        oomp_deets = {}
        import hashlib
        md5 = hashlib.md5(current_entry_name.encode()).hexdigest() 
        oomp_deets["md5"] = md5
        #trim md5 to 6 and add it as md5_6
        oomp_deets["md5_5"] = md5[0:5]
        #add to md5_5 dict
        md5_6 = md5[0:6]
        oomp_deets["md5_6"] = md5_6
        oomp_deets["md5_10"] = md5[0:10]

        oomp_deets["symbol_name"] = symbol_name
        oomp_deets["library_name"] = library_name
        oomp_deets["owner_name"] = owner_name

        oomp_deets['oomp_key'] = f'oomp_{symbol_name}'
        oomp_deets['oomp_key_extra'] = f'oomp_symbol_{symbol_name}'
        oomp_deets['oomp_key_full'] = f'oomp_symbol_{symbol_name}_{md5_6}'
        oomp_deets['oomp_key_simple'] = f'{symbol_name}'

        symb2["oomp"] = oomp_deets

        pass

        with open(f'{directory_name}/working.yaml', 'w') as f:
            yaml.dump(symb2, f)

    print()

def get_repo_from_github(**kwargs):
    rep = kwargs['repo']
    url = rep['url']
    if url in github_repos:
        return github_repos[url]
    else:
        #fetch the repo details from github api using requests
        import requests
        #get the repo details
        #get owner from url
        owner = url.split('/')[3]
        #get repo from url
        repo = url.split('/')[4]

        api_url = f'https://api.github.com/repos/{owner}/{repo}'
        #get the repo details
        r = requests.get(api_url)
        #convert to json
        repo = r.json()
        #add the repo to the github repos
        github_repos[url] = repo
        return repo
    
        
def make_symbols_readme():
    counter = 1
    folders = ["symbols_flat"]
    for folder in folders:
        #go through all the files in folder 
        for root, dirs, files in os.walk(folder):
            #if its a directory
            if os.path.isdir(root):
                #if it's called working
                if root.endswith('working'):
                    #load the working.yaml file from the folder
                    #try:
                        with open(f'{root}/working.yaml', 'r') as yaml_file:
                            yaml_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
                        #create a readme file by calling make_readme(yaml_dict)
                        readme = make_readme(yaml_dict=yaml_dict)
                        #save readme as readme.md
                        with open(f'{root}/readme.md', 'w') as readme_file:
                            try:
                                readme_file.write(readme)
                            except Exception as e:
                                print(f'error creating readme for {root} most likely no working.yaml file/n')
                                print(e)
                            pass
                        counter += 1
                        #print a dot every 100 times through
                        if counter % 100 == 0:
                            print('.', end='', flush=True)

                    #except Exception as e:
                    #    print(f'error creating readme for {root} most likely no working.yaml file/n')
                    #    print(e)
                    #    pass
    print()

def make_readme(**kwargs):
    yaml_dict = kwargs['yaml_dict']
    #if yaml_dict is an array take element
    if type(yaml_dict) is list:
        yaml_dict = yaml_dict[0]

    yaml_table =  oom_base.yaml_to_markdown(**kwargs)
    name = yaml_dict.get('name', '')
    owner = yaml_dict.get('owner', '')
    
    ## links
    links = yaml_dict.get('links', '')
    url = ""
    github_path = ""
    if links != '':
        url = links.get('github_src_repo', '')
        github_path = links.get('github_src', '')
        
    
    readme = f"""# {name} by {owner}  
This is a harvested standardized copy of a symbol from github.  
The original project can be found at:  
{url}  
The original symbol can be found in:
{github_path}
Please consult that link for additional, details, files, and license information.  
## yaml dump  
{yaml_table}
"""
    return readme