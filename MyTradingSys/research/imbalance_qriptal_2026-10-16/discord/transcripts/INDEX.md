# Qriptal (Habib) updates after 2026-09-30: transcripts and trade statements

Fetched 2026-10-16. Method for all six: `yt-dlp --skip-download --write-auto-subs --write-subs --sub-langs "en.*" --sub-format vtt` on `https://www.youtube.com/watch?v=<id>` (public YouTube captions, no cookies, login or key). The `en-orig` auto-caption track was returned; the translated `en` track failed with HTTP 429, which does not matter. Metadata (title, timestamp) from `yt-dlp --flat-playlist` and `--print` on the channel pages `/videos` and `/streams`. VTT rolling-caption cues were converted to one `[m:ss] text` line per new caption line (same line format as `extracts/_staged_2026-09-27/raw/qriptal_*_raw.txt`, no header block, as in those files). Publish time is the yt-dlp `timestamp` (UTC); for the two live streams it is the VOD time, not necessarily the stream start.

Excluded: 14PZEEbHSaM (2026-09-29, before the cutoff). The 13 Oct update is RW-Nn3e29Es. The 6 listed are the 6 newest videos or streams on the channel with publish date after 2026-09-30.

Caveats: captions are YouTube ASR, so words and numbers can be wrong (examples: 'RD imbalance', '386.2 two stop loss', 'job' for 'drop'). Quotes are the caption lines joined verbatim with the [m:ss] markers removed; a range can start or end mid-sentence because captions are cut by time. 'Price not stated' means no price is in the quoted lines; nothing is inferred. Section selection was done by reading each transcript in full; if a statement looks missing, grep the raw file.

| id | title | published (UTC) | URL | type | method | raw file |
|---|---|---|---|---|---|---|
| f9nuENfR-2o | Bitcoin: CRASH incoming?! | 2026-10-15 12:47:19 | https://www.youtube.com/watch?v=f9nuENfR-2o | YouTube update, 543 s | yt-dlp en-orig vtt | qriptal_f9nuENfR-2o_raw.txt |
| RW-Nn3e29Es | Bitcoin: Once again, exactly as predicted... | 2026-10-13 12:51:48 | https://www.youtube.com/watch?v=RW-Nn3e29Es | YouTube update (Tuesday 13 Oct), 683 s | yt-dlp en-orig vtt | qriptal_RW-Nn3e29Es_raw.txt |
| sLaymf4LB_8 | Bitcoin: Make or Break RIGHT NOW! | 2026-10-06 12:09:01 | https://www.youtube.com/watch?v=sLaymf4LB_8 | YouTube update, 494 s | yt-dlp en-orig vtt | qriptal_sLaymf4LB_8_raw.txt |
| bnqojhZrFNQ | Bitcoin: BOTH of our plans played out (perfectly)! | 2026-10-01 11:51:11 | https://www.youtube.com/watch?v=bnqojhZrFNQ | YouTube update, 668 s | yt-dlp en-orig vtt | qriptal_bnqojhZrFNQ_raw.txt |
| Y0YZnyUCtuM | Bitcoin LIVE analysis and weekly outlook - Are we ready for 90k? | 2026-10-12 07:32:05 | https://www.youtube.com/watch?v=Y0YZnyUCtuM | live stream (weekly outlook), 3215 s | yt-dlp en-orig vtt | qriptal_Y0YZnyUCtuM_raw.txt |
| B6ImdQNCFTI | Bitcoin LIVE analysis and weekly outlook - The Correction is near... | 2026-10-04 18:53:01 | https://www.youtube.com/watch?v=B6ImdQNCFTI | live stream (weekly outlook), 2509 s | yt-dlp en-orig vtt | qriptal_B6ImdQNCFTI_raw.txt |

## f9nuENfR-2o: Bitcoin: CRASH incoming?! (2026-10-15 12:47 UTC)

### Habib's own trade statements and plans
Tags: ENTRY/STOP/TP/RESULT = executed trade; NOT-TAKEN = he says he did not trade; PLAN/TARGET = stated plan or hypothetical, not an executed trade.

- [0:55] **NOT-TAKEN** (waiting for entry that did not come): "won't be too much to recap inside of the Discord because I just didn't do much. I was waiting for the move up into 85.5 to open that short position, which didn't come. So with that said, with today's"
- [2:25] **TARGET** (ETH, plan only): "it could be already time to look for swing trading longs at least on Ethereum. Now, personally, I'll be honest, my bigger target is 2,250, which would be an ideal target in my opinion to open much better swing longs."
- [6:02] **PLAN** (hypothetical long, generic 'you'): "you could very simply wait for the New York open. And let's say you get a reclaim of the daily open. This is a trade that is that is possible. Let's say you get a reclaim of this. You go for your stop loss maybe below that low. And then you just aim for a move into 85.5, something like this."
- [7:53] **PLAN** (long under consideration, not taken): "Personally, I'll be honest, I'm not even sure if I will take that long position. However, it's the only thing that I can see. So, depending on the volume, maybe I'll take it, maybe I won't. Honestly, I"
- [8:13] **PLAN** (long target area): "just break down from here, personally, I would be very happy, honestly, because it would just mean a faster job into $73,000, where personally, I am looking for a very big long position. So, that is a"

Count: 5.

### Imbalances named (timeframe and price exactly as in the quote)

- [1:59]: "Looking at the volume, it is pretty good because now you have two 12-hour imbalances. Let me just fix the daily open, so we don't have a daily imbalance yet. But we do have two 12-hour imbalances, and on the 4-hour we don't have an imbalance, however."
- [4:34]: "volume isn't the best. I have to admit, if you look at the 4-hour, can even go over to Binance. We don't have any 4-hour imbalance. We don't have a 12-hour imbalance both on Bybit and Binance. Even on the 1-hour, we just have one already imbalance, and even then, the wick is extremely ugly. So,"

## RW-Nn3e29Es: Bitcoin: Once again, exactly as predicted... (2026-10-13 12:51 UTC)

### Habib's own trade statements and plans
Tags: ENTRY/STOP/TP/RESULT = executed trade; NOT-TAKEN = he says he did not trade; PLAN/TARGET = stated plan or hypothetical, not an executed trade.

- [1:15] **NOT-TAKEN** (short missed (asleep)): "not putting an alert, but overall, I was not able to take that short because once again, I was asleep. And very quickly,"
- [2:05] **ENTRY+STOP** (long): "At this point I was still eyeing the Sunday plan plus we had two hourly imbalances right on support. So personally I did decide to take the long position with a stop loss at 81,500."
- [2:22] **RESULT** (long stopped out): "happened today as happened last week. I got stopped out of my long position and then if I go over to the chart so I got"
- [2:36] **RESULT** (bounce after stop-out): "Beautiful bounce as well. It's a bounce of about 3 and 1/2% so very very good returns especially for a swing trade. If"
- [2:45] **RESULT** (previous week's short): "you guys remember last week it was the exact same thing. I had taken the short stop loss 86.6. I got taken out and then we got a massive reversal to the downside. So two weeks in a row where"
- [4:43] **PLAN** (expects move, no trade yet): "For me, I am still expecting a move into around $85,500."
- [8:39] **PLAN** (short plan): "I am still expecting a move into 85.5. I am still expecting this to offer resistance. This is where I would look for a short position. And ideally, we"
- [9:24] **PLAN** (short rule): "But, overall, for myself, I am not interested in any short position above 85.5. In my opinion, this is a key"
- [9:57] **PLAN** (short plan): "This is where I want to look for a short position this week, if we can get it,"

Count: 9.

### Imbalances named (timeframe and price exactly as in the quote)

- [1:23]: "see, we did have a beautiful 4-hour imbalance into that level. So, very easy short. We talked about it on Sunday that I wanted to see one more sweep above that high. We got one more sweep above that high. We got the 4-hour imbalance, so that was beautiful. Personally, once"
- [2:05]: "At this point I was still eyeing the Sunday plan plus we had two hourly imbalances right on support. So"
- [5:21]: "add back the volume profile, we had a 4-hour imbalance on Binance, but we also had the point of control of this entire range. So, as you can see,"
- [6:05]: "main confluence will always be the imbalances. Remember what this level was? It was a 4-hour imbalance on Binance. Bybit, you can see"
- [6:21]: "going back over to to Bybit, what do we have up there? We have a 4-hour imbalance and we also have a 12-hour imbalance. I don't think we have a daily. Yeah, we don't have a daily on Binance as well. So we don't have a daily imbalance up there, but we do have 12-hour and a 4-hour."

## sLaymf4LB_8: Bitcoin: Make or Break RIGHT NOW! (2026-10-06 12:09 UTC)

### Habib's own trade statements and plans
Tags: ENTRY/STOP/TP/RESULT = executed trade; NOT-TAKEN = he says he did not trade; PLAN/TARGET = stated plan or hypothetical, not an executed trade.

- [0:30] **PLAN** (short plan from live): "personally, what I had said in the live stream very quickly is I was not interested in a short on the weekly open, but I wanted to wait for the Monday New York open to look for a short position on a retest. Now, as we got"
- [0:52] **NOT-TAKEN** (short skipped): "I wasn't as confident in the short position on the New York open, which ended up being a mistake because from"
- [1:07] **PLAN** (long at support): "interested in long a support below just because of all of these highs above around $85,200. Okay, so that was my support if we were able to drop into it, I was interested in a long position. Now, when we got the"
- [1:21] **NOT-TAKEN** (long not taken): "drop, I was still interested in a long position, but I was just waiting for a bit more volume because if you go on the 30-minute chart, we just didn't have a nice imbalance down there. And unfortunately,"
- [1:43] **NOT-TAKEN** (reason no long): "the chart, and I add back the support, which was very simply a 4-hour imbalance, and this 4-hour order block. So, if you take a trade there, as you can see what I was looking at at the time is that we had this job and the 4-hour close right at the low, okay? On top of that, we didn't have a 1-hour imbalance, we didn't have a 3-minute imbalance, so I just didn't have much to open that long position."
- [2:10] **RESULT** (assessment): "Unfortunately, the idea to look for a long was right, but the support wasn't as accurate as usual and the volume, to be honest, wasn't the best. However, very quickly"
- [3:29] **ENTRY** (previous week's short): "we had a 4-hour imbalance right there, which was also the weekly open. We moved up into it, I took the short, we got a rejection to the downside, and as I had"
- [4:46] **NOT-TAKEN** (no short yet): "Now, have I taken a short? Not yet, because just like yesterday, okay, I would like to see a 30-minute imbalance right here. If we don't have a 30-minute or a 1-hour, in my opinion, the short position is not a valid. Just like right"
- [5:54] **PLAN** (short trigger): "get an imbalance right now, my bad. So, if we are able to get an imbalance right now, I think this could trigger a short position for the Sunday plan to fully play out and see the reversal lower into $81,000,"
- [6:14] **PLAN** (short trigger, resistance level): "complicated. This week, I have just one resistance left on Bitcoin, and it is right here around $86,300. We are moving up into it. However, presently, I am waiting for an imbalance, as usual, to trigger a short position. If we have an imbalance, I will be more than happy to take a short and see the reversal to the downside."
- [6:52] **RESULT** (long attempt unfilled): "even. Unfortunately, yesterday, the support wasn't the most accurate, but also, I just didn't have the volume on the first job. On the second job, super unfortunate, but I was asleep right there. So, I mean, I tried to catch that long position just because we had all of that liquidity above. So, right now, it's"
- [7:46] **PLAN** (short trigger): "update. Very simple. I am waiting for the imbalance to appear. If we get it, I am going to trigger a short position. If we don't get it, no short position, and that's mainly it. So, with that said, as"

Count: 12.

### Imbalances named (timeframe and price exactly as in the quote)

- [2:18]: "wasn't the best. However, very quickly this morning we got the 30-minute imbalance finally, which was also a 1-hour imbalance. Personally, unfortunately, I wasn't awake, but if anyone was awake, that was a very acceptable long position, especially that it was a wickless imbalance, so you have the imbalance, you have the wickless candle, that was that it was a retest of support as well. Acceptable long position to see that reversal to the upside."
- [3:29]: "we had a 4-hour imbalance right there, which was also the weekly open. We moved up into it, I took the short, we got a rejection to the downside, and as I had"
- [4:24]: "me. On top of that, so we have a 4-hour imbalance, we have a 1-hour imbalance, so you can take this, and right in between them we have a wickless 30-minute imbalance. And as you can see,"
- [5:42]: "imbalance right here, either on Bybit or on Binance, we can go over to Binance so I show you. We don't have an imbalance yet on Binance. On the 1-hour, we don't have an imbalance as well. So, if we are able to"

## bnqojhZrFNQ: Bitcoin: BOTH of our plans played out (perfectly)! (2026-10-01 11:51 UTC)

### Habib's own trade statements and plans
Tags: ENTRY/STOP/TP/RESULT = executed trade; NOT-TAKEN = he says he did not trade; PLAN/TARGET = stated plan or hypothetical, not an executed trade.

- [1:05] **ENTRY+STOP** (aggressive short): "was Tuesday, I think. So, yeah, on Tuesday, I had taken the aggressive short against the weekly open. We had we were seeing the test of that level at once again 84.4 with an imbalance. So personally I took an aggressive short position with a hard stop loss at $84,800."
- [1:22] **STOP** (stop moved to local high): "After that price went sideways for about 2 hours. We got one more sweep and when we got into the New York open I decided to move my stop loss against the local high. Okay. So placing stop loss on the current high because I kind of didn't"
- [1:36] **RESULT** (price moved down): "want to see a new high made. In the end, that was the right decision because that high did uh end up holding and we got a very nice move to the downside once again testing $82,800."
- [1:50] **TP** (no TP1, stop to break even): "So from there it was fairly simple. It was a good place to implement a take profit one but for myself I did want to be a bit more aggressive and I did not want to implement a take-profit one. However, of course, I moved my stop loss to break even just because I was very confident that price would drop lower. I"
- [2:19] **RESULT** (stopped out at break even): "we did end up holding these lows. We got yet another move to the upside. Got stopped out at break even of my short position and the next level was of course $85,600"
- [2:30] **NOT-TAKEN** (next short skipped): "still. However, personally I skipped that short position even though we hadn't reached that level yet. If I zoom in, we hadn't reached that level yet. But for me, I skipped the short position just because it looked like a strong breakout to me. And to be honest, I was"
- [5:47] **TP** (reason no TP): "and that was the main reason I did not want to implement a take profit on my short position because at this point when I didn't take u uh a TP1 it was a"
- [6:23] **TP** (reason no TP): "our bigger resistance. Okay, so that's just quickly why I didn't really want to implement a take profit one on my short position. But any in any case, as you"
- [8:55] **PLAN** (long take-profit idea): "is a fairly big drop. However, if we take the long position and we see strength then we can simply implement a take profit one up here for example. And if we see strength, you can just hold on"
- [9:50] **PLAN** (long idea): "The most obvious the most obvious plan for me would be a sweep of this double top before coming back down into that level. And from there, of course, we can see what happens. If we get volume and the reaction, this can offer a long position. And from there, we can see"

Count: 10.

### Imbalances named (timeframe and price exactly as in the quote)

- [1:11]: "were seeing the test of that level at once again 84.4 with an imbalance. So personally I took an aggressive short"
- [6:12]: "imbalance. We had an imbalance. We had three imbalances there. So people were really aggressive on on shorting their breakdowns, which is why in the end we"
- [7:20]: "monthly pivot below us. we have a wickless 4hour imbalance. This hasn't changed. But now on top of that, we have"

## Y0YZnyUCtuM: Bitcoin LIVE analysis and weekly outlook - Are we ready for 90k? (2026-10-12 07:32 UTC)

### Habib's own trade statements and plans
Tags: ENTRY/STOP/TP/RESULT = executed trade; NOT-TAKEN = he says he did not trade; PLAN/TARGET = stated plan or hypothetical, not an executed trade.

- [3:21] **ENTRY** (short on 30 minute imbalance): "was doing the update that was the YouTube update, price was literally testing our resistance at $86,300 and all I was waiting for for the short position was either a 30 minute imbalance or an R imbalance. You asked me in the general chat and I told you that I had taken the short as we did get a deep 30 minute imbalance right here right on the New York open as well. So personally I took my short position and"
- [3:54] **STOP** (stop at the high, stopped out): "sweep a rejection a second sweep a rejection a third sweep with an imbalance on the New York open and a fourth rejection and I thought at this point that we had trapped enough people. So when I saw this rejection, I put my stop loss at this high and I actually left home. And when I came back, I saw that I had been stopped out before getting that reversal to the downside, which was pretty annoying this week. I"
- [4:19] **RESULT** (short result and stop): "have to admit, I even share my exchange. I mean, just to be transparent. I took the short when we got this 30 minute imbalance. I just showed you the candle. I got stopped out on this candle and then we got the reversal to the downside and 386.2 two stop loss at the high which was 8 86.5 again [snorts] not the best management from myself I will have to admit however"
- [5:00] **RESULT** (swing long not taken, bounce 4%): "one thing that that I didn't fully get I will admit was the swing long position because in my opinion as we're getting the drops into $81,000. Okay, so into our level even though the volume was good for me swing longs were not really valid. Of course I ended up being wrong because from the low depending on your entry of course but from the low we are now up 4%. For a swing trade 4% is pretty good. Okay, it's amazing actually"
- [6:21] **ENTRY** (position statement): "action. My short is now at 85.5. I added a little to it. Okay, we've covered the"
- [7:58] **NOT-TAKEN** (long not taken, bounce): "the 4hour imbalance. Plus for the long if anyone wanted to take it. I mean we had two 30 minute imbalances right there. So that was a valid long. But for me usually it's very rare that I trade uh the end of the week plus the weekend. Usually I don't trade this. But as you can see, you had the volume for a potential quick long position, which ended up offering a great bounce into $84,000. But any case, with that said,"
- [8:56] **NOT-TAKEN** (not short): "week, I think. Now, personally, very quickly, I am not short, but as usual, I don't love trading the weekend. So, I prefer just like last week, even though"
- [9:15] **NOT-TAKEN** (no weekend trade): "annoying. It's pretty volatile. So here the same thing. Um I'm not going to trade uh the weekend even though acceptable short position. But"
- [13:46] **PLAN** (target 12hour imbalance and long idea): "this is quite complicated. And then I would target this week probably a fill of this 12hour imbalance at 85.5 just because yes, even though we are moving into a critical area, I'm not really seeing the biggest trap. Even though we have a nice wig, I'm not seeing a second early imbalance and it is right before the weekly open, which I am not the biggest fan of. So I think that we could get this if we get a rejection on the weekly open probably a drop into this level and then I could aim for a long position to to look for a move up into 85.5"
- [15:57] **PLAN** (long idea / target): "see one more sweep into the open. If we get a job there, this is where we could look for a long position. In my opinion, that's what I would aim for this week. On the other hand, if we got a drop, we don't have the best volume or the best reaction, then very simply, I will personally aim for 72 to $73,000."
- [29:16] **PLAN** (how he traded the week (generic you)): "do as we did this week, you find a resistance as we had at 86.3. You take the short, you look for that move down, you take profits, you let the rest run or however you guys want to ma want to manage this short position. But you get"
- [30:20] **PLAN** (short consideration): "get it on the on the open. I'll see. I don't I wouldn't mind actually looking for the short now if we get it."
- [39:44] **NOT-TAKEN** (could have shorted): "And see now this rejection is turning into a bigger one if anyone shorted the first retest. So good level. Can see good level. The volume coming in. I could have shorted this. Honestly, I"
- [49:12] **PLAN** (drop target then long): "this high to get taken out, which is the logic behind this plan, it dropped potentially into 81.8. From there, I would look for a move back up. Technically, it doesn't have to be above 85.5. We can just take this high and and"

Count: 14.

### Imbalances named (timeframe and price exactly as in the quote)

- [1:21]: "access to my imbalance indicator, which once again gave us the high of this week with two RD imbalances, the low was a bit harder to catch as you will see, but we had very good volume with a 4hour imbalance. Once again, the link will be"
- [7:10]: "important area on buy bit. We don't have much but on Binance we have a 4hour imbalance right there. Okay. So remember"
- [7:27]: "moved into this 4hour imbalance and it is offering quite I mean a decent rejection for now on the lower time frames. Plus this is not the only confluence. If you take the volume profile of this range as you can see we are also testing the point of control of the range that we broke it down of. As you can see with the value area low, we got the bounce into Friday. We got a retest of the value area low and from there we are now moving into the point of control which is in confluence with the 4hour imbalance. Plus for the long if anyone wanted to take it. I mean we had two 30 minute imbalances right there. So that was a valid long. But for"
- [8:25]: "now, we have the 4hour imbalance. The 12-hour, we don't have much. On the daily, we don't have much. What about the 3day? We don't have much. So, it's just a 4hour imbalance and the point of"
- [11:01]: "time. I have to be honest. We have a 1 hour imbalance down there. Do we have a 4 hour? So, we have a 4hour order block, but no imbalance. No imbalance. Man, this is a hard one."
- [12:44]: "and see the support is just a 1 hour imbalance on the 4hour order block. It's unfortunate that we don't have the"
- [13:46]: "this is quite complicated. And then I would target this week probably a fill of this 12hour imbalance at 85.5 just because yes, even though we are"
- [20:36] (ETH): "time on Ethereum. O, look at that volume. Actually, we have two 4hour imbalances. Okay, that's big. That is big. So, am I happy with the plan on"
- [26:36] (ZEC): "terms of support. You had the daily imbalance to be fair. Look, look at the accuracy. I mean, daily imbalance. You literally frontr run it by a cent, but would you really call this a front? Look at this. I mean, pretty much got hit with the dollar. So, I'm not really going to call this a front. Pretty much can't get more accurate than that. Fill off the daily imbalance and the reversal higher. And on top of that, you have the 4hour wickless. 4hour wickless candle dropped into it plus the daily imbalance. It's offering the bounce."
- [29:36]: "look at this. We now have a 4hour imbalance, a second 4hour imbalance. So that would greatly reinforce my plan. I'm happy with that plan now because we have much better volume. So maybe one more sweep into the weekly open and then it offers that drop into 81.8. That is great. That is great. So yeah, you have the level now which is remember 4hour imbalance on Binance. On Bybit you have great volume with a second 4hour imbalance. And finally, of course, a very big confluence. You have the point of control of the entire"
- [38:10]: "up. I mean, look at the volume. A daily imbalance on the drop. Even there 4hour imbalance on the breakdown. two 4hour imbalances. So even though it might be"
- [48:15]: "technically you could call this reclaim of the range, we are we are still testing and rejecting actually a pretty major level which is the range point of control which is also a 4hour imbalance on Binance and you can see it is offering the rejection. The small problem that I have with this even though now we got the second 4hour imbalance is that we are rejecting right"

## B6ImdQNCFTI: Bitcoin LIVE analysis and weekly outlook - The Correction is near... (2026-10-04 18:53 UTC)

### Habib's own trade statements and plans
Tags: ENTRY/STOP/TP/RESULT = executed trade; NOT-TAKEN = he says he did not trade; PLAN/TARGET = stated plan or hypothetical, not an executed trade.

- [2:41] **ENTRY+STOP** (aggressive short, TP1 skipped, stop to break even): "was kind of leaning towards the weekly high being in. I did the Tuesday update where where we had a resistance at 84.4. I decided to take my short position at 84.4. [clears throat] Okay, aggressive short with a stop loss at 84.8. After that, we did get an extremely nice rejection to the downside of 2%. But personally, I decided not to implement a take-profit one and move my stop loss to break even. It's a bit laggy indeed. But"
- [3:23] **RESULT** (stopped out, next short skipped): "know, man. Sorry for this. So, yeah, we took the short, got a very nice rejection, but from there, we were seeing a reversal to the upside. Here I just decided to remain short and chill with my stop loss still to break even. I then got stopped out of my short. We moved higher towards 85.6. Once again, I decided to skip this short position and then it ended up being an extremely"
- [3:55] **NOT-TAKEN** (Thursday sweep short not taken): "much. We had a short that I shared in the in the Thursday update which was a sweep above this double top at at 84.4. But when we got the first rejection, personally I didn't want to short. Okay, I didn't want to short yet first because we had a a scam on Binance at 84.7."
- [4:18] **NOT-TAKEN** (short not taken): "about this in the general chat why personally I didn't really really want to short yet even though we did have a bit of volume and another rejection above that high but once again personally I didn't take the short and after that we just ended up moving much"
- [15:33] **TARGET** (plan, not short): "frame drops. I think that's what I would look for is the upside on the weekly open and then reversed to the downside targeting once again $81,400ish."
- [16:37] **NOT-TAKEN** (not shorted yet): "you have a short. Personally, I haven't shorted yet. I am thinking about it, but I would just like to wait for the for the weekly open because the problem with shorting here is that even though you"
- [16:57] **PLAN** (hypothetical short, generic you): "because of the timing? You could go for a short like this maybe like that would be your entry. Maybe stop loss right there and then a reversal lower. That is acceptable, but"
- [20:00] **NOT-TAKEN** (no short on Friday): "to trap more people to the upside. I'll be honest, I am not super sure, which is why I didn't short on Friday, even though we did have very good volume. I was so close to bre to to pressing the short button up here, but I just wasn't super confident in that um in that position, which was a mistake in the end. That was a great job. But you"
- [28:00] **TARGET** (LIT, imbalance and double top): "Well, locally you do have a partially filled 4hour imbalance with a double top at 3.7. Okay, so this is a very good target. This is more for lower time frame analysis. You have a double top and you have a 4hour imbalance. So if you took the long then I would hold it"
- [31:09] **PLAN** (LIT hypothetical long with RR): "You would put the order here stop loss I would pick this low and then targeting the highs. But that's a three 4 to one. It's 4 to1 the best thing on low"
- [31:38] **STOP** (LIT stop): "say. So that's why you I'm picking this stop loss just below $3. Okay. If you wanted to play it a bit more"
- [40:40] **NOT-TAKEN** (not short): "I'm not short. I'm probably not going to short around the weekly open because I'm probably going to be asleep. The best thing to do is to let it play out. wake"

Count: 12.

### Imbalances named (timeframe and price exactly as in the quote)

- [2:26]: "had pretty insane volume on Binance with three 4hour imbalances. If I open the chart, as you will see, we had three 4hour imbalances on this drop, which was quite crazy. As mentioned above, it did"
- [7:32]: "imbalances. Can even go on the 30 minutes. We had two imbalances there. Another imbalance here. two other imbalances here. Uh this this wasn't that bad, but I mean if you understand imbalances, that was not ideal. We had three imbalances there. And we had yet two more imbalances right there. So pretty much what's happening is that on every single job, you get the job, what"
- [9:08]: "we can add back the support that I removed by mistake. We have a 4hour wickless imbalance down there. So we can dig the support. We have a monthly pivot"
- [10:08]: "We have a wick loss for our imbalance and still as we have been talking about this week, we have an obvious level"
- [12:22]: "We have two 4hour imbalances up here. So, do you want to short? I mean you can"
- [15:03]: "Binance. So if you take this, this is what interesting about this about this area is that you have a 4hour imbalance and over on buy bit you have two 4hour imbalances on this move up. So can you already look for a short position? I'll"
- [20:23]: "had the volume with the RD imbalance. You had a wickless uh 1 hour imbalance below. You had a wickless 30 minute, you had a super ugly imbalance, and you had a wickless 30 minute imbalance on Binance if I'm not mistaken. No, you didn't. You had a wickless candle right there. So yeah, you had nice conference, but personally I didn't take it. So"
- [28:00] (LIT): "Well, locally you do have a partially filled 4hour imbalance with a double top at 3.7. Okay, so this is a very good target. This is more for lower time frame analysis. You have a double top and you have a 4hour imbalance. So if"
- [33:30] (NEAR): "your target. You have a partially filled 4hour imbalance. So if near wants to offer a retest to the downside,"

