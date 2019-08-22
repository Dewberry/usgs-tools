import pandas as pd
from StreamStats_ID_Points import *


def main(pourpoint: tuple, df: pd.DataFrame, display: bool = False):
    """
    Function that moves up a stream network from the pourpoint and identifies
    the conflunce pairs.
    :param pourpoint:
    :param df:
    :param display:
    :return:
    """
    # Empty list to store the stream cells that we do not want to return to
    # since we have already searched them
    nogo = []
    # Empty list to store the identified confluence pairs
    confluence_pairs = []
    # Empty list to store the original location of the confluence pairs
    confluence_pairs_orig = []
    # Empty list to store the location of confluences that are three cells
    # away from the original confluence location
    save_confluence = []
    # The confluence number or ID
    cnum = 0
    # Counting variable. The number of times we have looped over the while
    # loop below
    count = 0
    # The starting point of the stream network where we want to start searching
    # for confluences. Add the confluence number
    starting_point = pourpoint[0] + (cnum,)
    # Add the starting point to the no go list
    nogo.append(starting_point)

    while len(starting_point) > 0:
        count += 1
        cnum = count
        next_cell = MoveUpstream(df, starting_point, nogo, cnum)
        if len(next_cell) == 1:
            nogo.append(next_cell[0])
            starting_point = next_cell[0]
        else:
            if len(next_cell) > 1:
                nogo = nogo + next_cell
                confluence_pairs += next_cell
                confluence_pairs_orig += next_cell
                if display and float(cnum / 100.0).is_integer():
                    print(f'Confluence Number: {cnum}')
            if len(confluence_pairs) > 0:
                starting_point = confluence_pairs[0]
                confluence_pairs.remove(starting_point)
                cnum = starting_point[2]
                i = 0
                while i < 2:
                    next_cell = MoveUpstream(df, starting_point, nogo, cnum)
                    if len(next_cell) == 1:
                        nogo.append(next_cell[0])
                        starting_point = next_cell[0]
                        i += 1
                        continue
                    elif len(next_cell) > 1:
                        confluence_pairs += next_cell
                        confluence_pairs_orig += next_cell
                        i = 2
                    elif len(next_cell) == 0:
                        i = 2
                if len(next_cell) == 1:
                    save_confluence.append(starting_point)
            else:
                starting_point = []
    return save_confluence, confluence_pairs_orig, nogo


if __name__ == "__main__":
    main()
