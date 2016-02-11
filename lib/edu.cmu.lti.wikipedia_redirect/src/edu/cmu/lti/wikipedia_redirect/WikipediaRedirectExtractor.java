/*
 * Copyright 2011 Carnegie Mellon University
 * Licensed under the Apache License, Version 2.0 (the "License"); 
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *  
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, 
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied. See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */
package edu.cmu.lti.wikipedia_redirect;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Extracts wikipedia redirect information and serializes the data.
 * 
 * @author Hideki Shima
 *
 */
public class WikipediaRedirectExtractor {

  private static String titlePattern    = "    <title>";
  private static String redirectPattern = "    <redirect";
  private static String textPattern     = "      <text xml";
  private static Pattern pRedirect = Pattern.compile(
          "#[ ]?[^ ]+[ ]?\\[\\[(.+?)\\]\\]", Pattern.CASE_INSENSITIVE);
  
  public void run( File inputFile, File outputFile ) throws Exception {
    int invalidCount = 0;
    long t0 = System.currentTimeMillis();
    FileInputStream fis = new FileInputStream( inputFile );
//    TreeMap<String,String> map = new HashMap<String,String>();
    InputStreamReader isr = new InputStreamReader(fis, "utf-8");
    BufferedReader br = new BufferedReader(isr);
    FileOutputStream fos = new FileOutputStream(outputFile);
    OutputStreamWriter osw = new OutputStreamWriter(fos, "utf-8");
    BufferedWriter bw = new BufferedWriter(osw);

    int count = 0;
    String title = null;
    String text = null;
    String line = null;
    boolean isRedirect = false;
    boolean inText = false;
    while ((line=br.readLine())!=null) {
      if (line.startsWith(titlePattern)) {
        title = line;
        text = null;
        isRedirect = false;  
      }
      if (line.startsWith(redirectPattern)) {
        isRedirect = true;
      }
      if (isRedirect && (line.startsWith(textPattern) || inText)) {
        Matcher m = pRedirect.matcher(line); // slow regex shouldn't be used until here.
        if (m.find()) { // make sure the current text field contains [[...]]
          text  = line;
          try {
            title = cleanupTitle(title);
            String redirectedTitle = m.group(1);
            if ( isValidAlias(title, redirectedTitle) ) {
              bw.write( title+"\t"+redirectedTitle+"\n" );
              count++;
//              map.put( title, redirectedTitle );
            } else {
              invalidCount++;
            }
          } catch ( StringIndexOutOfBoundsException e ) {
            System.out.println("ERROR: cannot extract redirection from title = "+title+", text = "+text);
            e.printStackTrace();
          }
        } else { // Very rare case 
          inText = true;
        }
      }
    }
    br.close();
    isr.close();
    fis.close();

    bw.close();
    osw.close();
    fos.close();
    System.out.println("---- Wikipedia redirect extraction done ----");
    long t1 = System.currentTimeMillis();
//    IOUtil.save( map );
    System.out.println("Discarded "+invalidCount+" redirects to wikipedia meta articles.");
    System.out.println("Extracted "+count+" redirects.");
    System.out.println("Saved output: "+outputFile.getAbsolutePath());
    System.out.println("Done in "+((t1-t0)/1000)+" sec.");
  }
  
  private String cleanupTitle( String title ) {
    int end = title.indexOf("</title>");
    return end!=-1?title.substring(titlePattern.length(), end):title;
  }

  /**
   * Identifies if the redirection is valid.
   * Currently, we only check if the redirection is related to
   * a special Wikipedia page or not.
   * 
   * TODO: write more rules to discard more invalid redirects.
   *  
   * @param title source title
   * @param redirectedTitle target title
   * @return validity
   */
  private boolean isValidAlias( String title, String redirectedTitle ) {
    if ( title.startsWith("Wikipedia:") 
            || title.startsWith("Template:")
            || title.startsWith("Portal:")
            || title.startsWith("List of ")) {
      return false;
    }
    return true;
  }
  
  public static void main(String[] args) throws Exception {
    if (args.length!=1) {
      System.err.println("ERROR: Please specify the path to the wikipedia article xml file as the argument.");
      System.err.println("Tips: enclose the path with double quotes if a space exists in the path.");
      return;
    }
    File inputFile = new File(args[0]);
    if (!inputFile.exists() || inputFile.isDirectory()) {
      System.err.println("ERROR: File not found at "+inputFile.getAbsolutePath());
      return;
    }
    String prefix = inputFile.getName().replaceFirst("-.*", "");
    File outputDir = new File("target");
    if (!outputDir.exists()) {
      outputDir.mkdirs();
    }
    File outputFile = new File(outputDir, prefix+"-redirect.txt");
    new WikipediaRedirectExtractor().run( inputFile, outputFile );
  }
}
