# these are broadly similar to the function in lib.combined.remove_stations
def remove_stations(f, station: str, df):
    idx_of_station = df[df['Station'] == station].index
    idxes_to_drop = f(idx_of_station[0], df.index)
    df.drop(index=idxes_to_drop, inplace=True)

def remove_stations_after_exclusive(station: str, df):
    '''remove stations after `station`, excluding `station`
    (meaning `station` won't be removed)'''
    remove_stations(lambda x, y: range(x + 1, y[-1] + 1), station, df)

