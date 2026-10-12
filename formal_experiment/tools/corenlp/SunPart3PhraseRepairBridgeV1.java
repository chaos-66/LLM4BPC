import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.tregex.TregexMatcher;
import edu.stanford.nlp.trees.tregex.TregexPattern;
import edu.stanford.nlp.trees.tregex.tsurgeon.Tsurgeon;
import edu.stanford.nlp.trees.tregex.tsurgeon.TsurgeonPattern;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
import java.util.*;

/** Project-owned bridge. Input: key, masked token indexes, original tree.
 * Every output indexes surviving original leaves; no span envelopes hide gaps.
 */
public final class SunPart3PhraseRepairBridgeV1 {
  public static void main(String[] args) throws Exception {
    int surgeries = 0;
    for (String line : Files.readAllLines(Paths.get(args[0]), StandardCharsets.UTF_8)) {
      String[] row = line.split("\t", 3);
      Tree tree = Tree.valueOf(row[2]);
      List<Tree> leaves = tree.getLeaves();
      IdentityHashMap<Tree,Integer> indexes = new IdentityHashMap<>();
      for (int i=0; i<leaves.size(); i++) indexes.put(leaves.get(i),i);
      if (!row[1].isEmpty()) for (String value : row[1].split(",")) {
        int index = Integer.parseInt(value);
        if (index<0 || index>=leaves.size()) throw new IllegalArgumentException("mask out of range");
        if (tree==null) break;
        Tree leaf = leaves.get(index);
        if (!tree.getLeaves().contains(leaf)) continue;
        String sentinel="SCOPE_REMOVAL_"+index;
        leaf.label().setValue(sentinel);
        TregexPattern pattern=TregexPattern.compile("/^"+sentinel+"$/=removed");
        TsurgeonPattern operation=Tsurgeon.parseOperation("prune removed");
        tree=Tsurgeon.processPattern(pattern,operation,tree);
        surgeries++;
      }
      if (tree==null) continue;
      for (String field : new String[]{"action","actor"}) {
        TregexPattern pattern=TregexPattern.compile((field.equals("action") ? "VP" : "NP")+"=candidate");
        TregexMatcher matcher=pattern.matcher(tree);
        while(matcher.find()) {
          Tree candidate=matcher.getNode("candidate");
          List<String> original=new ArrayList<>();
          for (Tree leaf : candidate.getLeaves()) {
            Integer index=indexes.get(leaf);
            if (index==null) throw new IllegalStateException("lost original leaf identity");
            original.add(index.toString());
          }
          System.out.println(row[0]+"\t"+field+"\t"+String.join(",",original));
        }
      }
    }
    System.err.println("Tsurgeon prune operations: "+surgeries);
  }
}
