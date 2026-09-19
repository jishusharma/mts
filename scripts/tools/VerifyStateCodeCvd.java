package datafeed;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.Deque;

public class VerifyStateCodeCvd {
    public static void main(String[] args) throws Exception {
        StateCodeEmitter em = new StateCodeEmitter("BTCUSDT");

        Method slope = StateCodeEmitter.class.getDeclaredMethod("computeCvdSlope", double.class);
        slope.setAccessible(true);
        Field seriesF = StateCodeEmitter.class.getDeclaredField("cvdSeries");
        seriesF.setAccessible(true);

        long day1 = 1_000L;
        long day2 = day1 + 86_400_000L;
        long day3 = day2 + 86_400_000L;

        int pass = 0, fail = 0;

        em.nowMsOverride = day1;
        for (int i = 0; i < 15; i++) slope.invoke(em, 100.0);
        int c1 = ((Deque<?>) seriesF.get(em)).size();
        if (c1 == 15) { pass++; System.out.println("PASS case1 ring=15 same-day accumulate"); }
        else { fail++; System.out.println("FAIL case1 ring=" + c1 + " expected 15"); }

        em.nowMsOverride = day2;
        slope.invoke(em, 200.0);
        int c2 = ((Deque<?>) seriesF.get(em)).size();
        if (c2 == 1) { pass++; System.out.println("PASS case2 ring=1 after day change"); }
        else { fail++; System.out.println("FAIL case2 ring=" + c2 + " expected 1"); }

        for (int i = 0; i < 4; i++) slope.invoke(em, 200.0);
        int c3 = ((Deque<?>) seriesF.get(em)).size();
        if (c3 == 5) { pass++; System.out.println("PASS case3 ring=5 same-day add"); }
        else { fail++; System.out.println("FAIL case3 ring=" + c3 + " expected 5"); }

        em.nowMsOverride = day3;
        slope.invoke(em, 300.0);
        int c4 = ((Deque<?>) seriesF.get(em)).size();
        if (c4 == 1) { pass++; System.out.println("PASS case4 ring=1 second day change"); }
        else { fail++; System.out.println("FAIL case4 ring=" + c4 + " expected 1"); }

        System.out.println("----");
        System.out.println("PASS=" + pass + "  FAIL=" + fail);
        if (fail > 0) System.exit(1);
    }
}