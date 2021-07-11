import logging, re, regex

logging.basicConfig(level=logging.DEBUG)

regex = r"#~^%/*-+<>"

def conversion(a,b):
    """Conversion function from type(b) to type(a)
    Args:
        a (str, int or float): var
        b (str, int or float): var

    Returns:
        str, int or float: return the b with new type or False if conversion failed
    """
    try:
        if isinstance(a, str):
            b = str(b)
        elif isinstance(a, int):
            b = int(b)
        elif isinstance(a, float):
            b = float(b)
        return b
    except ValueError:
        return False

def check_datas(liste_a_convertir, liste_de_test):
    if len(liste_a_convertir) == len(liste_de_test):
        for i in range(0, len(liste_a_convertir)):
            if type(liste_a_convertir[i]) != type(liste_de_test[i]):
                logging.info('CONVERSION')
                to_convert = conversion(liste_de_test[i], liste_a_convertir[i])
                if to_convert:
                    liste_a_convertir[i] = to_convert
        return liste_a_convertir
    return False

def cleanhtml(raw_html):
    """ This function remove the html balises and hexa digits
    Args:
        raw_html (string): any kind html string

    Returns:
        str : return a string without html balises and hexa digits
    """
    cleanr = re.compile('<.*?>')
    if type(raw_html) == str :
        cleantext = re.sub(cleanr, '', raw_html)
        #clean = "".join([elm for elm in cleantext if elm not in regex])
        return cleantext
    else :
        logging.warning(f'Cant clean {type(raw_html)}.')        
        return raw_html

if __name__ == "__main__":

    a = '<>/<<<>>~###^^&&&test'
    b = "-<A.T.A>-BlackDrago"
    c = "test test creation"
    d = "'DROP DATABASE creation;'"
    print(cleanhtml(a))
    print(cleanhtml(b))
    print(cleanhtml(d))

    #print(cleanhtml.__doc__)
