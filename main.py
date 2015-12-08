from instagram import InstagramAPI
from textblob import TextBlob
import matplotlib.pyplot as plt
import matplotlib.dates
import matplotlib.patches as mpatches
import mpld3
import pandas as pd

# Sets how many post to get
post_count = 100
# Creates a threshold for neutral post
neutral_min = 0.04
neutral_max = 0.215
min_subjectivity = 0.3
# Sets hashtag to be analyze (do no include the hashtag symbol)
hash_tag = 'cats'
# Set up Instagram API
client_id = '5214935bc88e4e598dd5ef7432ca7118'
client_secret = 'e6a3e426fa1e43108ae929ceebbc2c4f'
api = InstagramAPI(client_id=client_id, client_secret=client_secret)


def get_ids():
    # Get all ids for all post
    ids, next = api.tag_recent_media(tag_name=hash_tag, count=post_count)
    temp, max_tag = next.split('max_tag_id=')
    max_tag = str(max_tag)

    while next and len(ids) < post_count:
        more_ids, next = api.tag_recent_media(tag_name=hash_tag, count=max_tag)
        temp, max_tag = next.split('max_tag_id=')
        max_tag = str(max_tag)
        for id in more_ids:
            if len(ids) < post_count:
                ids.append(id)
    return ids


def get_post_data(ids):
    # Get post data for each post
    post_data = {}
    captions = []
    likes = []
    times = []
    for id in ids:
        captions.append((id.caption.text).encode('utf-8'))
        likes.append(id.like_count)
        times.append(id.created_time)
    post_data['captions'] = captions
    post_data['likes'] = likes
    post_data['times'] = times
    return post_data


def get_user_data(ids):
    # Get user data for each post
    user_data = {}
    post_counts = []
    follower_counts = []
    following_counts = []
    for id in ids:
        user_id = api.user(id.user.id)
        post_counts.append(user_id.counts['media'])
        follower_counts.append(user_id.counts['follows'])
        following_counts.append(user_id.counts['followed_by'])
    user_data['post_counts'] = post_counts
    user_data['follower_counts'] = follower_counts
    user_data['following_counts'] = following_counts
    return user_data


def get_posts_tones(ids):
    # Determine if each post is positivenegative, or neutral
    # green = positive, red = negative, grey = neutral
    tones = []
    for id in ids:
        text = TextBlob(id.caption.text.replace('#', ''))
        if text.sentiment.polarity > neutral_max and text.sentiment.subjectivity > min_subjectivity:
            tones.append('green')
        elif text.sentiment.polarity < neutral_min and text.sentiment.subjectivity > min_subjectivity:
            tones.append('red')
        else:
            tones.append('gray')
    return tones


def write_to_file(post_data):
    # Write data to a data file
    file = open('{0}-results.txt'.format(hash_tag), 'w')
    for i in range(len(post_data['ids'])):
        file.write('Post {0}\n'.format(i + 1))
        file.write('Caption: {0}\n'.format(post_data['captions'][i]))
        if post_data['tones'][i] == 'green':
            file.write('This post is positive\n')
        elif post_data['tones'][i] == 'red':
            file.write('This post is negative\n')
        else:
            file.write('This post is neutral\n')
        file.write('Likes: {0}\n'.format(post_data['likes'][i]))
        file.write('----------Poster Info----------\n')
        file.write('Post Count: {0}\n'.format(post_data['post_counts'][i]))
        file.write('Followers: {0}\n'.format(post_data['follower_counts'][i]))
        file.write('Following: {0}\n'.format(post_data['following_counts'][i]))
        file.write('\n')

    file.write('Total positive post {0}\n'.format(post_data['tones'].count('green')))
    file.write('Total negative post {0}\n'.format(post_data['tones'].count('red')))
    file.write('Total neutral post {0}\n'.format(post_data['tones'].count('grey')))
    file.close()


def vis_data(post_data):
    # Use Mpld3 to visualize data
    # CSS for labels
    css = """

    body {
      background-color: #E0E4CC
    }
    iframe {
      width: 80%
      height: 900%
      text-align: left
    }
    table, th, td, iframe
    {
      font-family: Arial, Helvetica, sans-serif;
      text-align: right;
      color: #000000;
      background-color: #A7DBD8;
      border: none;
      border-spacing: 0;
      padding: 0;
    }
    """
    pd.set_option('display.max_colwidth', -1)
    size = []
    for likes in post_data['likes']:
        if likes > 1:
            size.append(likes * 10)
        else:
            size.append(9)

    data = pd.DataFrame({
        'Color': post_data['tones']
    })
    labels = []
    for i in range(len(post_data['ids'])):
        label = data.ix[[i], :].T
        label.columns = ['Post {0}'.format(i + 1)]
        labels.append((label.to_html()))

    fig, ax = plt.subplots()

    scatter = ax.scatter(matplotlib.dates.date2num(post_data['times']),
                         post_data['follower_counts'],
                         c=post_data['tones'],
                         s=size,
                         alpha=0.7,
                         cmap=plt.cm.jet)
    ax.grid(color='white', linestyle='solid')

    ax.set_title('#{0} Trends'.format(hash_tag), size=40)
    green = mpatches.Patch(color='green', label='Positive')
    gray = mpatches.Patch(color='gray', label='Neutral')
    red = mpatches.Patch(color='red', label='Negative')
    plt.legend(handles=[green, gray, red], ncol=3, framealpha=0.5)
    plt.xlabel('Time', size=25)
    plt.ylabel('Number of Followers the Poster has', size=25)
    frame = plt.gca()
    frame.axes.get_xaxis().set_ticks([])
    frame.axes.get_yaxis().set_ticks([])

    tooltip = mpld3.plugins.PointHTMLTooltip(scatter, labels, css=css)
    mpld3.plugins.connect(fig, tooltip)

    fig.set_size_inches(8.5, 6.5)

    mpld3.save_html(fig, '{0}-graph.html'.format(hash_tag))


def append_html():
    # Add iframe containing post data to html file
    lines = []
    with open('{0}-graph.html'.format(hash_tag)) as ins:
        for line in ins:
            lines.append(line)

    lines.append('\n<iframe src="{0}-results.txt"\n'.format(hash_tag))
    lines.append('width=680px\n')
    lines.append('height=120px>\n')
    lines.append('</iframe>')

    file = open('{0}-graph.html'.format(hash_tag), 'w')
    for line in lines:
        print(line)
        file.write(line)
    file.close()


def main():
    global hash_tag
    hash_tag = raw_input('Enter a valid hashtag (without the # symbol): ')
    print('Gathering data')
    post_data = {}
    post_data['ids'] = get_ids()
    post_data.update(get_post_data(post_data['ids']))
    post_data.update(get_user_data(post_data['ids']))
    print('Analyzing data')
    post_data['tones'] = get_posts_tones(post_data['ids'])

    print('Creating text file')
    write_to_file(post_data)

    print('Creating HTML file')
    vis_data(post_data)
    append_html()


if __name__ == '__main__':
    main()
