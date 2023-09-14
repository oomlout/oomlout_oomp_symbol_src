import oomlout_oomp_symbol_src
import oom_kicad

def main():
    pass
    oomlout_oomp_symbol_src.clone_and_copy_symbols(test=True)
    oomlout_oomp_symbol_src.make_symbols_readme()
    oom_kicad.push_to_git()    





if __name__ == '__main__':
    main()