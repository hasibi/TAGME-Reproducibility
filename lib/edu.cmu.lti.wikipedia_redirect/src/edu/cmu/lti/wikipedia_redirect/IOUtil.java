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
import java.io.FileReader;
import java.io.InputStreamReader;
import java.io.LineNumberReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.OutputStreamWriter;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;

/**
 * Reads and writes wikipedia redirect data.
 * 
 * @author Hideki Shima
 *
 */
public class IOUtil {

  /**
   * Save Wikipedia redirect data
   * 
   * @param redirectData
   *   map where key is original term and value is redirected term
   * @throws Exception
   */
  public static void save( AbstractMap<String,String> map ) throws Exception {
    File outputDir = new File("target");
    if (!outputDir.exists()) {
      outputDir.mkdirs();
    }
    WikipediaRedirect wr = new WikipediaRedirect( map );
    saveText( wr, outputDir );
    saveSerialized( wr, outputDir );
  }
  
  /**
   * Save Wikipedia redirect data into tab separated text file
   * 
   * @param redirectData
   *   map where key is original term and value is redirected term
   * @throws Exception
   */
  private static void saveText( WikipediaRedirect wr, File outputDir ) throws Exception {
    File txtFile = new File(outputDir, "wikipedia_redirect.txt");
    FileOutputStream fosTxt = new FileOutputStream(txtFile);
    OutputStreamWriter osw = new OutputStreamWriter(fosTxt, "utf-8");
    BufferedWriter bw = new BufferedWriter(osw);
    for ( Entry<String,String> entry : wr.entrySet() ) {
      bw.write( entry.getKey()+"\t"+entry.getValue()+"\n" );
    }
    bw.close();
    osw.close();
    fosTxt.close();
    System.out.println("Saved redirect data in text format: "+txtFile.getAbsolutePath());
  }
  
  /**
   * Save Wikipedia redirect data into serialized object
   * 
   * @param redirectData
   *   map where key is original term and value is redirected term
   * @throws Exception
   */
  private static void saveSerialized( WikipediaRedirect wr, File outputDir ) throws Exception {
    File objFile = new File(outputDir, "wikipedia_redirect.ser");
    FileOutputStream fosObj = new FileOutputStream(objFile);
    ObjectOutputStream outObject = new ObjectOutputStream(fosObj);
    outObject.writeObject(wr);
    outObject.close();
    fosObj.close();
    System.out.println("Serialized redirect data: "+objFile.getAbsolutePath());
  }
  
  /**
   * Deserializes wikipedia redirect data
   * @param file 
   *   serialized object or tab-separated text
   * @return wikipedia redirect
   * @throws Exception
   */
  public static WikipediaRedirect loadWikipediaRedirect( File f ) throws Exception {
    if (!f.exists() || f.isDirectory()) {
      System.err.println("File not found: "+f.getAbsolutePath());
      System.exit(-1);
    }
    if ( f.getName().endsWith(".ser") ) {
      return loadWikipediaRedirectFromSerialized( f );
    } else {
      //faster than above?
      return loadWikipediaRedirectFromText( f );
    }
  }
  
  /**
   * Deserializes wikipedia redirect data from serialized object data
   * @param file 
   *   serialized object
   * @return wikipedia redirect
   * @throws Exception
   */
  private static WikipediaRedirect loadWikipediaRedirectFromSerialized( File f ) throws Exception {
    WikipediaRedirect object;
    try {
      FileInputStream inFile = new FileInputStream(f);
      ObjectInputStream inObject = new ObjectInputStream(inFile);
      object = (WikipediaRedirect)inObject.readObject();
      inObject.close();
      inFile.close();      
    } catch (Exception e) {
      throw e;
    }    
    return object;
  }
  
  /**
   * Deserializes wikipedia redirect data from tab-separated text file
   * @param file 
   *   tab-separated text
   * @return wikipedia redirect
   * @throws Exception
   */
  private static WikipediaRedirect loadWikipediaRedirectFromText( File f ) throws Exception {
    int size = (int)countLineNumber(f);
    WikipediaRedirect wr = new WikipediaRedirect( size );
    try {
      FileInputStream fis = new FileInputStream( f );
      InputStreamReader isr = new InputStreamReader( fis );
      BufferedReader br = new BufferedReader( isr );
      String line = null;
      while ( (line = br.readLine()) != null ) {
        String[] elements = line.split("\t");
        wr.put( elements[0], elements[1] );
      }
      br.close();
      isr.close();
      fis.close();
    } catch (Exception e) {
      throw e;
    }
    return wr;
  }
  
  /**
   * Loads tab separated data as an alternative way to load() method.
   * Works for Wikipedia hypernym data generated by
   * <a href="http://alaginrc.nict.go.jp/hyponymy/index.html">NICT's "Hyponymy extraction tool"</a>
   * 
   * @param file
   *   tab separated file that contains lines that look "word1[TAB]word2[BR]"
   * @return wikipedia redirect
   * @throws Exception
   */
  public static WikipediaHypernym loadWikipediaHypernym( File f ) throws Exception {
    int size = (int)IOUtil.countLineNumber( f );
    WikipediaHypernym object = new WikipediaHypernym( size );
    try {
      FileInputStream inFile = new FileInputStream( f );
      InputStreamReader isr = new InputStreamReader( inFile );
      BufferedReader br = new BufferedReader( isr );
      String line = null;
      while ( (line = br.readLine())!=null ) {
        String[] tokens = line.split("\t");
        if (tokens.length<=1) {
          continue;
        }
        String key = tokens[0];
        List<String> targets = object.get(key);
        if ( targets==null ) {
          targets = new ArrayList<String>();
        }
        targets.add(tokens[1]);
        object.put(key, targets);
      }
      br.close();
      isr.close();
      inFile.close();      
    } catch (Exception e) {
      throw e;
    }    
    return object;
  }
  
  /**
   * Count number of lines in a file in an efficient way
   * @param f
   * @return
   * @throws Exception
   */
  public static long countLineNumber( File f ) throws Exception {
    LineNumberReader lnr = new LineNumberReader(new FileReader(f));
    lnr.skip(Long.MAX_VALUE);
    int count = lnr.getLineNumber();
    lnr.close();
    return count;
  }
}
