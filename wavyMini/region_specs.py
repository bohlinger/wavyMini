''' 
dict for regions, currently defined by lat(e/w) lon(s/n) borders.
llcrnrlon=12.2,llcrnrlat=67.6,urcrnrlon=13.2,urcrnrlat=67.9
Ultimately, a shape file or polygon would be preferred.
Polygones are given as dict below. For Vietnam polygon approach 
has been disabled but examples are left here for orientation.
'''
region_dict = {"Global":            {
                                    "llcrnrlon":-180,
                                    "llcrnrlat":-90,
                                    "urcrnrlon":180,
                                    "urcrnrlat":90
                                    },
                "Vietnam":          {
                                    "llcrnrlon":99.0,
                                    "llcrnrlat":2.0,
                                    "urcrnrlon":120.0,
                                    "urcrnrlat":24.0
                                    },
                "Arctic":           {
                                    "boundinglat":66,
                                    },
                }

# - for larger regions polygons need to be defined with dense points 
#   along the borders to avoid a misrepresentation
# - the order of the points matter!
poly_dict = {"NorwegianSea": {
                "lats":[62.1,62.3,63.2,64.7,68.5,71.1,72.6,74.0,76.9,\
                        76.3,74.5,70.2,68.3,66.0,64.1,62.1],
                "lons":[5.1,-0.8,-6.6,-9.6,-8.6,-7.5,1.7,8.5,7.2,16.8,\
                        18.7,22.6,18.4,14.7,11.7,5.1]
                            },
             "BarentsSea": {
                "lats":[70.6,74.4,76.5,80.1,80.2,80.7,77.0,74.6,70.6,\
                        69.4,67.4,66.3,70.6],
                "lons":[21.9,18.7,16.7,27.7,37.5,52.3,67.3,57.7,56.8,\
                        61.2,50.3,43.12,21.9]
                            },
            "NordicSeas": {
                "lats":[62.1,61.9,62.3,64.3,66.2,68.6,70.4,73.4,76.2,79.5,79.5,79.5,76.6,74.4,72.4,70.5,69.1,68.0,66.2,64.3,62.5,62.1],
                "lons":[5.1,-0.9,-6.3,-14.8,-27.0,-34.8,-34.9,-34.39,-32.8,-30.0,0.5,11.0,17.4,19.0,20.5,22.5,22.5,18.2,15.4,12.8,9.5,5.1]
                            },
            }
