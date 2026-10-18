import subprocess,re,sys
def run(a): return subprocess.run(['yt-dlp']+a,capture_output=True).stdout.decode('utf8','replace')
for l in open('playlists.txt','rb').read().decode('utf8','replace').splitlines():
    pid,t=l.split('|',1)
    out=run(['--flat-playlist','--print','%(id)s|%(title)s','https://www.youtube.com/playlist?list='+pid])
    open('pl/'+pid+'.txt','w',encoding='utf8').write(out)
    ls=out.splitlines(); hid=sum(1 for x in ls if re.search(r'\|(\[Private video\]|\[Deleted video\]|NA)$',x))
    print(len(ls),hid,pid,t.encode('ascii','replace').decode())
ids=[l.split('|')[0] for l in open('videos.txt','rb').read().decode('utf8','replace').splitlines()]
print('DATES')
for i in list(range(0,len(ids),150))+[len(ids)-1]:
    print(i,ids[i],run(['--skip-download','--print','%(upload_date)s',ids[i]]).strip())
