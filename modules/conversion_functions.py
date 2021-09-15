import logging, re, regex
#import sanitize

logging.basicConfig(level=logging.DEBUG)

regex = r"#~^%/*-+<>"

def cleanhtml(raw_html: str) -> str:
    """ This function remove the html balises and hexa digits
    Args:
        raw_html (string): any kind html string

    Returns:
        str : return a string without html balises and hexa digits
    """
    regex = r"FROM|DATABASE|TABLE"

    cleanr = re.compile('<.*?>')
    cleanSQL = re.compile(regex)
    if type(raw_html) == str :
        cleantext = re.sub(cleanr, '', raw_html)
        cleantext = re.sub(cleanSQL, '', cleantext)
        return cleantext
    else :
        logging.warning(f'Cant clean {type(raw_html)}.')        
        return raw_html

if __name__ == "__main__":

    a = '<>/<<<>>~###^^&&&test'
    b = "-<test><test><<><o"
    c = "test test"
    d = "liphepvzêve <<fvf f !! fd f><creation<<< FROM DATABASE TABLE;'"
    print(cleanhtml(a))
    print(cleanhtml(b))
    print(cleanhtml(c))
    print(cleanhtml(d))
