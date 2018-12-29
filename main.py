from fb_crawl import FacebookCrawler
import time
import csv
import pandas as pd
import argparse
import sys

def main():

    if len(sys.argv)<4 :
        print("Need user and password for Facebook and Event ID")
        return 0

    crawler  = FacebookCrawler(sys.argv[1],sys.argv[2])
    crawler.login()
    event_id = str(sys.argv[3])
    info = crawler.access_event(event_id)
    to_csv("participants"+event_id, info['participants'])
    get_stats_event(event_id,info)



def get_stats_event(event_id, info):
    df = pd.DataFrame(info['participants'])
    print("Total participants:",info["num_going"])
    print("Total interested:",info["num_interested"])
    num_men = len(df[df['gender'] =="male"])
    num_women = len(df[df['gender'] =="female"])
    num_na = len(df[df['gender'] =="unknown"])
    num_going = info["num_going"]
    print("Total women", num_women)
    print("Share women", round(num_women/num_going*100),"%")
    print("Total men", num_men)
    print("Share men", round(num_men/num_going*100),"%")
    print("Total unknown", num_na)
    print("Share unknown", round(num_na/num_going*100),"%")



    df_c = df.groupby(['gender']).size().reset_index(name='counts')

    plot = df_c.plot.pie(labels=["female","male","n/a"],y='counts',figsize=(5, 5))

    fig = plot.get_figure()

    fig.savefig("./results/stats"+event_id+".png")

def to_csv(file_name, data):
    keys = data[0].keys()
    with open("./results/"+file_name+'.csv', 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)

if __name__ == "__main__":
    main()