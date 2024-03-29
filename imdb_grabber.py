from BeautifulSoup import BeautifulSoup
import re
import urllib2, urllib

def getNumFromString(num_string):
    number = int(''.join(i for i in num_string if i.isdigit()))
    #convert it to integer and return ...
    if number != '':
        return int(number)
    else:
        return 0



def removeHtmlReservedCharacters(html_string):
    return re.sub("(&#*\w+;)", "",html_string)

#from imdb_grabber import removeHtmlReservedCharacters as rhrc

def setIMDBEpisodeListLink(imdb_title_id):
    return "http://www.imdb.com/title/" + imdb_title_id + "/episodes"
    
def grabIMDBEpisodeList(imdb_title_id):
    series_dict = {}
    tds = None
    series_name = None
    try:
        page_url = setIMDBEpisodeListLink(imdb_title_id)
        #page_url = setIMDBEpisodeListLink("tt0903747")
        page = urllib2.urlopen(page_url)
        html = page.read()
        soup = BeautifulSoup(html)
        series = soup.find("div", { "id" : "tn15title"})
        series = series.find("a")
        series_name = series.find(text=True)

        #grab all <td> with valign attribute set to top
        tds = soup.findAll("td" , { "valign" : "top"})
    except urllib2.HTTPError:
        print "Unable to reach the site."
        return 0
    except urllib2.URLError:
        print "Wrong url."
        return 0
    except Exception:
        return 0

    series_dict["title"] = removeHtmlReservedCharacters(series_name)
    series_dict["seasons"] = []
    for td in tds:
        imdb_link = ''
        season_info = ''
        season_no = ''
        episode_no = ''
        air_date = ''
        title = ''
        description = ''
        season_head=td.find("h3")

        #if no <h3> then you get the episode info
        if not season_head:
            season_head =''
        if season_head:
            #get title
            title = season_head.find("a")
            title = title.find(text=True)
            imdb_link = "http://www.imdb.com" + str(season_head.find("a")["href"])

            #get episode air date
            air_date =td.find("strong")
            air_date = air_date.find(text=True)

            #get season no, episode no
            season_info= season_head.find(text=True)
            season_no = getNumFromString(str(season_info).replace(':','').split(',')[0])
            episode_no = getNumFromString(str(season_info).replace(':','').split(',')[1])

            #get description...
            description = str(td).replace(str(season_head), '').replace(str(td.find("span")), '') #remove <h3> and <span>
            tdp = BeautifulSoup(str(description)) #rerender it to BeautifulSoup
            description = tdp.find(text=True) #get only description

        if description.strip() == '':
            description = None

        if season_head:
            if episode_no == 1:
                series_dict["seasons"].append({})
                series_dict["seasons"][season_no-1]={ "no": str(season_no), "title" : "", "episodes": [] }
            

            episode = {}
            episode["no"] = episode_no
            episode["title"] = title
            episode["air_date"] = air_date
            episode["imdb_link"] = imdb_link
            episode["description"] = description
            
            series_dict["seasons"][season_no-1]["episodes"].append(episode)
            
            #print "\n\ntitle: ", title
            #print "air date: ", air_date
            #print "season no: ", season_no
            #print "episode no: ", episode_no
            #print "episode link: ", imdb_link
            #print "episode description: ", desc

    print "Series Name: ", removeHtmlReservedCharacters(series_name)
    return series_dict

def main():
    #ep_list = grabIMDBEpisodeList("tt0903747") #Breaking bad...
    #ep_list = grabIMDBEpisodeList("tt1405406") #vampire diaries...
    ep_list = grabIMDBEpisodeList("tt0898266") #Big bang theory...
    print "Total seasons: ", len(ep_list["seasons"])
    for season in ep_list["seasons"]:
        print "  Total episodes in Season ", season["no"],": ", len(season["episodes"])
        for episode in season["episodes"]:
            print "    No.: ", episode["no"], ", Title: ", episode["title"], ", Air date: ", episode["air_date"], ", IMDB Episode Link: ", episode["imdb_link"]

if __name__ == '__main__':
    main()