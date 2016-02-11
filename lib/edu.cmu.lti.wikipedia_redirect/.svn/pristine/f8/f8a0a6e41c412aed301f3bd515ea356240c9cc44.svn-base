package edu.cmu.lti.wikipedia_redirect;
import java.io.File;
import java.util.Set;

/**
 * Demo of what you can do with Wikipedia Redirect.
 * @author Hideki Shima
 */
public class Demo {
  private static String[] enSrcTerms = {"Bin Ladin", "William Henry Gates", 
    "JFK", "The Steel City", "The City of Bridges", "Da burgh", "Hoagie", 
    "Centre", "3.14"};
  private static String[] jaSrcTerms = {"オサマビンラディン", "オサマ・ビンラーディン",
          "東日本大地震","東日本太平洋沖地震" ,"NACSIS", 
          "ダイアモンド", "アボガド", "バイオリン", "平成12年", "3.14"};
  private static String enTarget = "Bayesian network";
  private static String jaTarget = "計算機科学";
  
  public static void main(String[] args) throws Exception {
    // Initialization
    System.out.print("Loading Wikipedia Redirect ...");
    long t0 = System.currentTimeMillis();
    File inputFile = new File(args[0]);
    WikipediaRedirect wr = IOUtil.loadWikipediaRedirect(inputFile);
    boolean useJapaneseExample = inputFile.getName().substring(0, 2).equals("ja");
    String[] srcTerms = useJapaneseExample ? jaSrcTerms : enSrcTerms;
    String target = useJapaneseExample ? jaTarget : enTarget;
    long t1 = System.currentTimeMillis();
    System.out.println(" done in "+(t1-t0)/1000D+" sec.\n");
    
    // Let's find a redirection given a source word.
    StringBuilder sb = new StringBuilder();
    for ( String src : srcTerms ) {
      sb.append("redirect(\""+src+"\") = \""+wr.get(src)+"\"\n");
    }
    long t2 = System.currentTimeMillis();
    System.out.println(sb.toString()+"Done in "+(t2-t1)/1000D+" sec.\n--\n");

    // Let's find which source words redirect to the given target word.
    Set<String> keys = wr.getKeysByValue(target);
    long t3 = System.currentTimeMillis();
    System.out.println("All of the following redirect to \""+target+"\":\n"+keys);
    System.out.println("Done in "+(t3-t2)/1000D+" sec.\n");
  }
}
