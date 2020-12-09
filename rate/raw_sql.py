ports_query = """
    WITH ports AS (
        WITH RECURSIVE c AS (
            SELECT '{port}'::varchar AS code UNION ALL SELECT r.slug
            FROM regions AS r JOIN c ON c.code = r.parent_slug
        ) (
            SELECT code from ports where code='{port}' or parent_slug
            in (SELECT code FROM c)
        )
    ) SELECT * from ports"""


average_price_query = """
    SELECT '' as id, day, 
        CASE WHEN COUNT(day) < 3 AND {rates_null} 
        THEN NULL 
        ELSE ROUND(AVG(price)::numeric,0) END as average_price
    FROM prices where orig_code in ({origin_ports})
    AND dest_code in ({destination_ports}) AND 
    day BETWEEN '{date_from}' AND '{date_to}' GROUP BY day ORDER BY day"""


average_price_query_with_null = """
"""
