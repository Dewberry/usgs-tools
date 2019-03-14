import sys
import pandas as pd
sys.path.append('scripts')
from StreamStats_Points import*


def main(pourpoint: tuple, df: pd.DataFrame):
	''' Function that moves up a stream network from the pourpoint and identifies the conflunce pairs.
	'''

	nogo=[] #Empty list to store the stream cells that we do not want to return to since we have already searched them
	confluence_pairs=[] #Empty list to store the identified confluence pairs
	confluence_pairs_orig=[] #Empty list to store the original location of the confluence pairs
	save_confluence=[] #Empty list to store the location of confluences that are three cells away from the original confluence location
	cnum=0 #The confluence number or ID
	count=0 #Counting variable. The number of times we have looped over the while loop below
	
	starting_point=pourpoint[0]+(cnum,) #The starting point of the stream network where we want to start searching for confluences. Add the confluence number

	nogo.append(starting_point) #Add the starting point to the no go list

	while len(starting_point)>0:
		count+=1
		cnum=count

		next_cell=MoveUpstream(df, starting_point, nogo, cnum)

		if len(next_cell) == 1:
			nogo.append(next_cell[0])
			starting_point = next_cell[0]
		else:
			if len(next_cell)>1:
				nogo=nogo+next_cell
				confluence_pairs+=next_cell
				confluence_pairs_orig+=next_cell
			if len(confluence_pairs)>0:
				starting_point=confluence_pairs[0]
				confluence_pairs.remove(starting_point)
				cnum=starting_point[2]

				i=0
				while i<2:
					next_cell=MoveUpstream(df, starting_point, nogo, cnum)

					if len(next_cell) == 1:
						nogo.append(next_cell[0])
						starting_point = next_cell[0]
						i+=1
						continue
					elif len(next_cell)>1:
						confluence_pairs+=next_cell
						confluence_pairs_orig+=next_cell						
						i=2
					elif len(next_cell)==0:
						i=2
				if len(next_cell) == 1:
					save_confluence.append(starting_point)
			else:
				starting_point=[]
	return save_confluence, confluence_pairs_orig, nogo

if __name__== "__main__":
	main()
    