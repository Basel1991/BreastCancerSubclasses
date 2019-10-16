import numpy as np
import pandas as pd

def encoder(hormone1, hormone2, hormone3):
    """
    encoder(hormon1, hormon2, hormon3)
    this function takes the status of three hormones and encodes them in Binary.
    example: hormone1 = 'RN', hormone2='RP', hormone3='RP', code=6
    any 'RU' value will return false.

    Inputs:
    -------
    hormone1: str, hormone1 status (the most significant bit)
    hormone2: str, hormone2 status
    hormone3: str, hormone3 status

    Returns:
    --------
    code: int, the code representing the three hormones
           -1 if any hormone is undefined or has the value 'RU'
    """
    hormones = np.array([hormone1, hormone2, hormone3])

    # generate the weights (exponents of two from MSB to LSB)
    multiplicand = np.arange(2, -1, -1)

    for horm in hormones:
        if pd.isna(horm) or horm == 'RU':
            print('Hormone undefined')
            return -1

    else:
        return np.dot(hormones == 'RP', 2 ** multiplicand)