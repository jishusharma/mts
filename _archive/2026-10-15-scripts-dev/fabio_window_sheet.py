import cv2,sys,numpy as np
vid=sys.argv[1];a=int(sys.argv[2]);b=int(sys.argv[3]);st=int(sys.argv[4]);tag=sys.argv[5]
cap=cv2.VideoCapture('F:/MTS/data/fabio_videos/%s.f398.mp4'%vid)
cells=[]
for t in range(a,b,st):
    cap.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,fr=cap.read()
    if not ok: continue
    fr=cv2.resize(fr,(960,540));cv2.putText(fr,"%s t=%d"%(vid,t),(10,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2);cells.append(fr)
while len(cells)%4: cells.append(np.zeros_like(cells[0]))
for i in range(0,len(cells),4):
    g=cells[i:i+4];cv2.imwrite('F:/MTS/data/fabio_videos/lowres/%s_%s_%02d.jpg'%(vid,tag,i//4),np.vstack([np.hstack(g[:2]),np.hstack(g[2:])]),[cv2.IMWRITE_JPEG_QUALITY,85])
