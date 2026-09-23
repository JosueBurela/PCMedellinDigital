\copy (SELECT row_to_json(t) FROM (SELECT * FROM "Message") t) TO stdout;
