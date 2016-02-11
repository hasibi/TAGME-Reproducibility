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

import java.io.Serializable;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;

/**
 * Represents the wikipedia redirect data.
 * 
 * Things you should know: key-value is one-to-many in Wikipedia Redirect.
 * Let's denote X -> Y when a source term X redirects to the term B.
 * X is unique in the entire Wikipedia Redirect data set, but Y is not.
 * In other words, there exists a Y such that X -> Y and X' -> Y. 
 * 
 * @author Hideki Shima
 *
 */
public class WikipediaRedirect extends HashMap<String,String>
 implements Serializable {
  //Do we need case insensitive hash map? C.f. http://www.coderanch.com/t/385950/java/java/HashMap-key-case-insensitivity

  private static final long serialVersionUID = 20111008L;

  public WikipediaRedirect() {
    super();
  }

  public WikipediaRedirect( int size ) {
    // RAM (heap) efficient capacity setting
    super( size * 4 / 3 + 1 );
  }

  public WikipediaRedirect( Map<String, String> map ) {
    super( map );
  }

  /**
   * Get keys in the map such that the value equals to the given value.
   *   
   * @param value
   * @return keys
   */
  public Set<String> getKeysByValue(String value) {
    Set<String> results = new LinkedHashSet<String>();
    //Iterating through all items is slow.
    //TODO: use existing library for faster access e.g. guava.
    for (Entry<String,String> entry : entrySet()) {
      if (value.equals(entry.getValue())) {
        results.add(entry.getKey());
      }
    }
    return results;
  }
}
