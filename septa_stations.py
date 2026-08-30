"""
SEPTA rail station coordinates and Philadelphia geography reference points.

These are hardcoded on purpose. SEPTA does not publish a stable public station
feed (their ArcGIS endpoints 404, and the city's Carto instance has no station
table), but station locations effectively never move. Coordinates are accurate
to roughly a city block, which is well inside the tolerance of a
"is this walkable to transit?" question.

Covered: Market-Frankford Line (all), Broad Street Line (all), and the Regional
Rail stations that sit inside the city limits.
"""

# City Hall - the reference point for "center of the city".
CITY_HALL = (39.9524, -75.1635)

STATIONS = [
    # --- Market-Frankford Line (the "El") ---
    ("69th Street Transportation Center", "MFL", 39.9607, -75.2594),
    ("Millbourne", "MFL", 39.9629, -75.2531),
    ("63rd Street", "MFL", 39.9617, -75.2456),
    ("60th Street", "MFL", 39.9613, -75.2390),
    ("56th Street", "MFL", 39.9608, -75.2312),
    ("52nd Street", "MFL", 39.9603, -75.2237),
    ("46th Street", "MFL", 39.9576, -75.2131),
    ("40th Street", "MFL", 39.9560, -75.2020),
    ("34th Street", "MFL", 39.9556, -75.1918),
    ("30th Street", "MFL", 39.9553, -75.1836),
    ("15th Street", "MFL", 39.9524, -75.1646),
    ("13th Street", "MFL", 39.9515, -75.1608),
    ("11th Street", "MFL", 39.9511, -75.1578),
    ("8th Street", "MFL", 39.9508, -75.1531),
    ("5th Street / Independence Hall", "MFL", 39.9497, -75.1487),
    ("2nd Street", "MFL", 39.9491, -75.1434),
    ("Spring Garden (MFL)", "MFL", 39.9615, -75.1400),
    ("Girard (MFL)", "MFL", 39.9707, -75.1339),
    ("Berks", "MFL", 39.9782, -75.1290),
    ("York-Dauphin", "MFL", 39.9840, -75.1258),
    ("Huntingdon", "MFL", 39.9893, -75.1230),
    ("Somerset", "MFL", 39.9938, -75.1200),
    ("Allegheny (MFL)", "MFL", 39.9990, -75.1170),
    ("Tioga", "MFL", 40.0040, -75.1140),
    ("Erie-Torresdale", "MFL", 40.0110, -75.1090),
    ("Church", "MFL", 40.0180, -75.1040),
    ("Margaret-Orthodox", "MFL", 40.0230, -75.1000),
    ("Arrott Transportation Center", "MFL", 40.0265, -75.0912),
    ("Frankford Transportation Center", "MFL", 40.0243, -75.0800),

    # --- Broad Street Line ---
    ("Fern Rock Transportation Center", "BSL", 40.0405, -75.1350),
    ("Olney Transportation Center", "BSL", 40.0342, -75.1425),
    ("Logan", "BSL", 40.0292, -75.1442),
    ("Wyoming", "BSL", 40.0231, -75.1451),
    ("Hunting Park", "BSL", 40.0164, -75.1462),
    ("Erie (BSL)", "BSL", 40.0090, -75.1477),
    ("Allegheny (BSL)", "BSL", 40.0002, -75.1494),
    ("North Philadelphia (BSL)", "BSL", 39.9959, -75.1503),
    ("Susquehanna-Dauphin", "BSL", 39.9884, -75.1516),
    ("Cecil B. Moore", "BSL", 39.9799, -75.1537),
    ("Girard (BSL)", "BSL", 39.9718, -75.1552),
    ("Fairmount", "BSL", 39.9673, -75.1562),
    ("Spring Garden (BSL)", "BSL", 39.9620, -75.1573),
    ("Race-Vine", "BSL", 39.9556, -75.1600),
    ("City Hall", "BSL", 39.9530, -75.1638),
    ("Walnut-Locust", "BSL", 39.9483, -75.1653),
    ("Lombard-South", "BSL", 39.9430, -75.1660),
    ("Ellsworth-Federal", "BSL", 39.9350, -75.1670),
    ("Tasker-Morris", "BSL", 39.9280, -75.1680),
    ("Snyder", "BSL", 39.9210, -75.1690),
    ("Oregon", "BSL", 39.9140, -75.1700),
    ("NRG", "BSL", 39.9060, -75.1720),

    # --- Regional Rail, city stations ---
    ("30th Street Station", "RR", 39.9556, -75.1820),
    ("Suburban Station", "RR", 39.9540, -75.1680),
    ("Jefferson Station", "RR", 39.9527, -75.1582),
    ("Temple University", "RR", 39.9812, -75.1495),
    ("North Philadelphia (RR)", "RR", 39.9985, -75.1520),
    ("Wayne Junction", "RR", 40.0220, -75.1600),
    ("University City", "RR", 39.9470, -75.1900),
    ("Germantown", "RR", 40.0330, -75.1730),
    ("Chelten Avenue", "RR", 40.0370, -75.1720),
    ("Tulpehocken", "RR", 40.0450, -75.1830),
    ("Upsal", "RR", 40.0480, -75.1900),
    ("Mount Airy", "RR", 40.0560, -75.1930),
    ("Sedgwick", "RR", 40.0600, -75.1960),
    ("Chestnut Hill East", "RR", 40.0720, -75.2020),
    ("Chestnut Hill West", "RR", 40.0770, -75.2070),
    ("Queen Lane", "RR", 40.0230, -75.1880),
    ("Manayunk", "RR", 40.0250, -75.2230),
    ("Wissahickon", "RR", 40.0180, -75.2050),
    ("East Falls", "RR", 40.0100, -75.1930),
    ("Allegheny (RR)", "RR", 40.0010, -75.1740),
    ("Fern Rock (RR)", "RR", 40.0400, -75.1360),
    ("Olney (RR)", "RR", 40.0340, -75.1420),
    ("Lawndale", "RR", 40.0450, -75.1030),
    ("Cheltenham", "RR", 40.0520, -75.0960),
    ("Ryers", "RR", 40.0590, -75.0790),
    ("Fox Chase", "RR", 40.0770, -75.0830),
    ("Olney Ave", "RR", 40.0340, -75.1400),
    ("Torresdale", "RR", 40.0330, -74.9820),
    ("Holmesburg Junction", "RR", 40.0230, -75.0100),
    ("Tacony", "RR", 40.0180, -75.0290),
    ("Bridesburg", "RR", 39.9990, -75.0680),
    ("North Broad", "RR", 39.9880, -75.1560),
    ("Overbrook", "RR", 39.9800, -75.2470),
    ("Wynnefield Avenue", "RR", 39.9880, -75.2200),
    ("Eastwick", "RR", 39.9010, -75.2350),
    ("Angora", "RR", 39.9420, -75.2350),
    ("Fernwood-Yeadon", "RR", 39.9350, -75.2560),
    ("49th Street", "RR", 39.9440, -75.2170),
    ("Darby", "RR", 39.9200, -75.2620),
    ("Curtis Park", "RR", 39.9060, -75.2790),
    ("Highland Park", "RR", 39.9330, -75.2700),
]
