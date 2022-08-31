

from token_handler import *




# get top 5 wine list
    
@app.route('/topfive', methods=['POST', 'GET'])
@token_required
def getopfive(current_user):
    
    # get JSON data
    inp_data = request.get_json()
    
    # get the top 5 matches
    cursor.execute("""SELECT
    t.w_name,
    t.w_link
    FROM
    wine_data w
    JOIN
    (SELECT 
    ms_id,
    w1_id,
    w2_id,
    m_score 
    FROM match_score
    UNION
    SELECT 
    ms_id,
    w2_id,
    w1_id,
    m_score 
    FROM match_score
    ) s ON w.w_id = s.w1_id
    JOIN
    wine_data t ON s.w2_id = t.w_id AND w.w_colour = t.w_colour
    WHERE w.w_link = %s
    AND s.in_stock = 1
    ORDER BY
    s.m_score DESC
    LIMIT 5
    """,(inp_data["in_url"],))
    match_lstr = cursor.fetchall()

    # generate output 
    output = []
    for match_lst in match_lstr:
        
        wine_data = {}
        wine_data["name"] = match_lst[0]
        wine_data["link"] = match_lst[1]
        output.append(wine_data)
    
    return jsonify({"wine_list" : output})




# find wine (using)

@app.route('/winelist', methods=['POST', 'GET'])
@token_required
def wineListSrch(current_user):

    # get JSON data
    inp_data = request.get_json()

    # handle inputs from JSON data 
    if(inp_data['in_w_name'] and inp_data['in_w_name'] != ''):
        # create results list
        match_lstr = []
        # set name search options
        full_name = inp_data['in_w_name']
        like_full_name = '%' + full_name + '%'
        # get exact match and match for anything containing exact string
        cursor.execute("""SELECT w_name, w_link, 1 AS ratr FROM wine_data WHERE w_name = %s
        UNION SELECT w_name, w_link, 4 AS ratr FROM wine_data WHERE w_name LIKE %s""",(full_name,like_full_name,))
        qres = cursor.fetchall()
        for res in qres:
            match_lstr.append(res)

        # get string length 
        st_lngth = len(full_name)
        # set counter
        lcountr = 0
        # loop through typos 
        while lcountr < st_lngth:
            srchstr = full_name[:lcountr] + '_' + full_name[lcountr + 1:]
            sinstr = '%' + srchstr + '%'
            # get results for typos
            cursor.execute("""SELECT w_name, w_link, 2 AS ratr FROM wine_data WHERE w_name LIKE %s
            UNION SELECT w_name, w_link, 5 AS ratr FROM wine_data WHERE w_name LIKE %s""",(srchstr,sinstr,))
            qres = cursor.fetchall()
            for res in qres:
                match_lstr.append(res)
            # set missed counter
            mcountr = 0
            # loop through missed character
            while mcountr < st_lngth:
                gpstr = srchstr[:mcountr] + '_' + srchstr[mcountr:]
                gpinstr = '%' + gpstr + '%'
                cursor.execute("""SELECT w_name, w_link, 3 AS ratr FROM wine_data WHERE w_name LIKE %s
                UNION SELECT w_name, w_link, 6 AS ratr FROM wine_data WHERE w_name LIKE %s""",(gpstr,gpinstr,))
                qres = cursor.fetchall()
                for res in qres:
                    match_lstr.append(res)
                # increase counter
                mcountr+=1
            #increase counter
            lcountr +=1
        
        # generate output 
        output = []
        for match_lst in match_lstr:
            
            wine_data = {}
            wine_data["name"] = match_lst[0]
            wine_data["link"] = match_lst[1]
            wine_data["rank"] = match_lst[2]
            output.append(wine_data)
        
        return jsonify({"search_list" : output})
    else:
        return jsonify({"search_list" : "No searh criteria supplied."})
