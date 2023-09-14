import oomlout_oomp_symbol_src as oom_oss

import oom_kicad

def main(**kwargs):
    oom_oss.clone_and_copy_symbols(test=True) ##also copies things
    oom_kicad.push_to_git(repo_directory = "C:/GH/oomlout_oomp_symbol_all_the_kicad_symbols")






if __name__ == '__main__':
    main()