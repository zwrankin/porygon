from shapely.geometry import Polygon
from scipy.spatial import Voronoi


def coords_to_voronoi_polygons(x, y):
    """
    Get voronoi cells of a set of lat/longs
    Parameters
    ----------
    x : array of latitudes
    y : array of longitudes

    Returns
    -------
    polygons  : list of shapely.Polygons
    """

    vor = Voronoi([i for i in zip(x, y)])
    
    polygons = []

    for i in range(len(vor.regions)-1):
        vertex_list = []
        point_index = vor.point_region[i]  # the order of vor.regions is NOT the same as input lat/long
        for x in vor.regions[point_index]:
            if x == -1:
                break
            else:
                vertex = vor.vertices[x]
                # vertex = (vertex[1], vertex[0])  # flip the order for geojson???
                vertex = (vertex[0], vertex[1])
            vertex_list.append(vertex)
        if len(vertex_list) >= 3:  # edge cells aren't enclosed
            polygons.append(Polygon(vertex_list))
        else:
            polygons.append(Polygon([]))

    return polygons
