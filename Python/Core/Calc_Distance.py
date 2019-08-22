import pandas as pd
from StreamStats_ID_Points import *


def main(df: pd.DataFrame, cellsize: int, true_confluence: list,
         false_points: list, confluence_pairs_orig: list):
    """
    Function to calculate the tributary length and the length between the
    points on the main stem
    :param df:
    :param cellsize:
    :param true_confluence:
    :param false_points:
    :param confluence_pairs_orig:
    :return:
    """
    tributary = []
    mainstem = []
    # Copy the true_confluence list, since we want to walk upstream of these
    # to calculate the length to the end of the trib or next confluence
    walk_confluence = true_confluence.copy()
    nogo = [walk_confluence[0]]
    # Assign the first confluence point to the starting_point
    starting_point = walk_confluence[0]
    # The total distance from the confluence point
    total_dis = 0.0
    count = 1
    # repeat = 0

    false_pointswocnum = remove_cnum(false_points)

    nogoabs = nogo.copy()

    while len(walk_confluence) > 0:
        next_cell = MoveUpstream(df, starting_point, nogo)

        if count == 1 and len(next_cell) != 0:
            total_dis = TrueDistance(starting_point, next_cell[0], cellsize)
            nogo.append(next_cell[0])
            starting_point = next_cell[0]
            count += 1
            continue

        elif 1 < count <= 2 and len(next_cell) != 0:  # 4?
            if any(x in next_cell for x in confluence_pairs_orig):
                starting_point = walk_confluence[0]
                total_dis = 0.0
                count = 1
                continue
            else:
                step_dis = TrueDistance(starting_point, next_cell[0], cellsize)
                total_dis = step_dis + total_dis
                nogo.append(next_cell[0])
                starting_point = next_cell[0]
                count += 1
                continue

        elif count > 2 and len(next_cell) == 1:
            step_dis = TrueDistance(starting_point, next_cell[0], cellsize)
            total_dis = step_dis + total_dis
            nogo.append(next_cell[0])
            starting_point = next_cell[0]
            count += 1
            continue

        elif len(next_cell) > 1 and count > 2:
            next_cellwocnum = remove_cnum(next_cell)
            # If any of the cells in next_cell are in false_confluence, then
            # find that cell and assign it to next cell
            if any(x in next_cellwocnum for x in false_pointswocnum):
                nogo = nogo + next_cell
                for cell in next_cell:
                    test_cell = MoveUpstream(df, cell, nogo)
                    if len(test_cell) == 0:
                        next_cell.remove(cell)
                step_dis = TrueDistance(starting_point, next_cell[0], cellsize)
                total_dis = step_dis + total_dis
                starting_point = next_cell[0]
                count += 1
                continue
            else:
                step_dis = TrueDistance(starting_point, next_cell[0], cellsize)
                total_dis = step_dis + total_dis
                mainstem.append(walk_confluence[0] + (total_dis,))
                walk_confluence.remove(walk_confluence[0])
                if len(walk_confluence) > 0:
                    total_dis = 0.0
                    nogoabs = nogoabs + nogo
                    starting_point = walk_confluence[0]
                    nogo = [starting_point]
                    # repeat = 0
                    count = 1
                else:
                    walk_confluence = []

        elif len(next_cell) == 0:
            tributary.append(walk_confluence[0] + (total_dis,))
            walk_confluence.remove(walk_confluence[0])
            if len(walk_confluence) > 0:
                total_dis = 0.0
                nogoabs = nogoabs + nogo
                starting_point = walk_confluence[0]
                nogo = [starting_point]
                # repeat = 0
                count = 1
            else:
                walk_confluence = []

    nogoabs = list(set(nogoabs))

    return tributary, mainstem, nogoabs


if __name__ == "__main__":
    main()
