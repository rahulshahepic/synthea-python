package org.synthea.parity.probes;

import com.google.gson.JsonArray;
import com.google.gson.JsonNull;
import com.google.gson.JsonObject;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.mitre.synthea.helpers.Config;
import org.mitre.synthea.helpers.SimpleCSV;
import org.mitre.synthea.helpers.SimpleYML;
import org.yaml.snakeyaml.Yaml;

/**
 * Probe for T05: Config, SimpleCSV and SimpleYML. Writes config.jsonl,
 * csv.jsonl and yml.jsonl into the output directory, plus the exact input
 * files (tricky.properties, malformed.properties, file-utf8.properties,
 * synthetic.yml) that the Python parity test replays against the ports.
 * Config is static and cumulative, so config.jsonl is written in strict
 * order: default snapshot, probe-set keys, getters, tricky loads.
 */
public class ConfigProbe {

  private interface StrCall {
    String run() throws Exception;
  }

  private static String err(Throwable e) {
    return "ERR:" + e.getClass().getSimpleName();
  }

  private static void strOrErr(JsonObject obj, String field, StrCall call) {
    try {
      obj.addProperty(field, call.run());
    } catch (Throwable e) {
      obj.addProperty(field, err(e));
    }
  }

  private static JsonObject rowJson(Map<String, String> row) {
    JsonObject obj = new JsonObject();
    for (Map.Entry<String, String> e : row.entrySet()) {
      if (e.getValue() == null) {
        obj.add(e.getKey(), JsonNull.INSTANCE);
      } else {
        obj.addProperty(e.getKey(), e.getValue());
      }
    }
    return obj;
  }

  private static JsonArray rowsJson(List<LinkedHashMap<String, String>> rows) {
    JsonArray arr = new JsonArray();
    for (LinkedHashMap<String, String> row : rows) {
      arr.add(rowJson(row));
    }
    return arr;
  }

  public static void main(String[] args) throws Exception {
    Path outdir = Paths.get(args[0]);
    Files.createDirectories(outdir);
    writeConfig(outdir);
    writeCsv(outdir);
    writeYml(outdir);
  }

  // ---------------------------------------------------------------- Config

  private static void getAs(PrintWriter w, String key) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "getAs");
    o.addProperty("key", key);
    String value = Config.get(key);
    if (value == null) {
      o.add("get", JsonNull.INSTANCE);
    } else {
      o.addProperty("get", value);
    }
    o.addProperty("getDef", Config.get(key, "DEF"));
    strOrErr(o, "double", () -> Double.toString(Config.getAsDouble(key)));
    strOrErr(o, "doubleDef", () -> Double.toString(Config.getAsDouble(key, 9.25)));
    strOrErr(o, "int", () -> Integer.toString(Config.getAsInteger(key)));
    strOrErr(o, "intDef", () -> Integer.toString(Config.getAsInteger(key, -7)));
    strOrErr(o, "long", () -> Long.toString(Config.getAsLong(key)));
    strOrErr(o, "longDef", () -> Long.toString(Config.getAsLong(key, -9L)));
    o.addProperty("bool", Boolean.toString(Config.getAsBoolean(key)));
    o.addProperty("boolDef", Boolean.toString(Config.getAsBoolean(key, true)));
    w.println(o.toString());
  }

  private static void writeConfig(Path outdir) throws Exception {
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(outdir.resolve("config.jsonl"), StandardCharsets.UTF_8))) {
      // 1. Default synthea.properties snapshot, names in String.compareTo order.
      List<String> names = new ArrayList<>(Config.allPropertyNames());
      names.sort(String::compareTo);
      for (String name : names) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "default");
        o.addProperty("key", name);
        o.addProperty("value", Config.get(name));
        w.println(o.toString());
      }

      // 2. Probe-set keys, then the getAs* matrix over interesting keys.
      Map<String, String> probeKeys = new LinkedHashMap<>();
      probeKeys.put("probe.int", "42");
      probeKeys.put("probe.negative", "-13");
      probeKeys.put("probe.double", "2.5");
      probeKeys.put("probe.exp", "1.0E7");
      probeKeys.put("probe.boolTrue", "true");
      probeKeys.put("probe.boolFalse", "anything");
      probeKeys.put("probe.bad", "abc");
      probeKeys.put("probe.long", "3000000000");
      probeKeys.put("probe.empty", "");
      for (Map.Entry<String, String> e : probeKeys.entrySet()) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "set");
        o.addProperty("key", e.getKey());
        o.addProperty("value", e.getValue());
        w.println(o.toString());
        Config.set(e.getKey(), e.getValue());
      }
      List<String> getAsKeys = new ArrayList<>(List.of(
          "generate.timestep", "generate.default_population",
          "physiology.generators.enabled", "exporter.fhir.us_core_version",
          "exporter.bfd.bene_id_start", "exporter.bfd.mbi_start",
          "generate.demographics.socioeconomic.weights.income", "no.such.key"));
      getAsKeys.addAll(probeKeys.keySet());
      for (String key : getAsKeys) {
        getAs(w, key);
      }

      // 3. Tricky java.util.Properties parsing, loaded as an InputStream
      //    (ISO-8859-1). The exact bytes are saved for the Python replay.
      String trickyText =
          "# a comment\n"
          + "! another comment\n"
          + "   # indented comment\n"
          + "\t! tab-indented comment\n"
          + "\n"
          + "   \n"
          + "tricky.eq = equals\n"
          + "tricky.colon: colon\n"
          + "tricky.space space value\n"
          + "tricky.tab\ttabbed value\n"
          + "tricky.nosep\n"
          + "tricky.empty =\n"
          + "tricky.empty2 : \n"
          + "tricky.spacesep    =    spaced value\n"
          + "tricky.mixed : value with : and = inside\n"
          + "tricky\\ key = escaped space key\n"
          + "tricky\\:colon = escaped colon key\n"
          + "tricky\\=eq = escaped equals key\n"
          + "escapes = a\\tb\\nc\\\\d\\\"e\\'f\\ g\\qh\n"
          + "uni = \\u0041\\u0042\\u00e9\n"
          + "\\u0074ricky.uni = unicode key value\n"
          + "\\u00e9key = e-acute key\n"
          + "cont = first \\\n        second \\\n\tthird\n"
          + "nocont = a\\\\\n"
          + "after.nocont = yes\n"
          + "dup = first\n"
          + "dup = second\n"
          + "trailing = value with trailing spaces   \n"
          + "lead.esc = \\ leading space value\n"
          + "\f\t leading.key = leading value\n"
          + "tricky.ff\fvalue ff\n"
          + "cr.line = crlf value\r\n"
          + "cr.only = cr value\r"
          + "next.after.cr = after cr\n"
          + "latin = café\n";
      byte[] trickyBytes = trickyText.getBytes(StandardCharsets.ISO_8859_1);
      Files.write(outdir.resolve("tricky.properties"), trickyBytes);
      JsonObject marker = new JsonObject();
      marker.addProperty("kind", "loadTricky");
      w.println(marker.toString());
      Config.load(new ByteArrayInputStream(trickyBytes));
      List<String> trickyKeys = new ArrayList<>(List.of(
          "tricky.eq", "tricky.colon", "tricky.space", "tricky.tab", "tricky.nosep",
          "tricky.empty", "tricky.empty2", "tricky.spacesep", "tricky.mixed",
          "tricky key", "tricky:colon", "tricky=eq", "escapes", "uni", "tricky.uni",
          "ékey", "cont", "nocont", "after.nocont", "dup", "trailing", "lead.esc",
          "leading.key", "tricky.ff", "cr.line", "cr.only", "next.after.cr", "latin"));
      trickyKeys.sort(String::compareTo);
      for (String key : trickyKeys) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "tricky");
        o.addProperty("key", key);
        String v = Config.get(key);
        if (v == null) {
          o.add("value", JsonNull.INSTANCE);
        } else {
          o.addProperty("value", v);
        }
        w.println(o.toString());
      }

      // 4. Malformed unicode escapes, each in its own load: bad hex digits,
      //    and a doubled-u escape (which JDK 21 loadConvert rejects).
      String[][] malformedCases = {
          {"badHex", "bad.key = \\u00xz\n"},
          {"doubleU", "bad.key = \\uu0042\n"},
          {"shortHex", "bad.key = \\u041\n"},
      };
      for (String[] mc : malformedCases) {
        byte[] malformedBytes = mc[1].getBytes(StandardCharsets.ISO_8859_1);
        Files.write(outdir.resolve("malformed-" + mc[0] + ".properties"), malformedBytes);
        JsonObject mo = new JsonObject();
        mo.addProperty("kind", "malformed");
        mo.addProperty("name", mc[0]);
        try {
          Config.load(new ByteArrayInputStream(malformedBytes));
          mo.addProperty("error", "NONE");
        } catch (Throwable e) {
          mo.addProperty("error", e.getClass().getSimpleName());
        }
        w.println(mo.toString());
      }

      // 5. The File overload: a UTF-8 file written into the output dir.
      Path cafe = outdir.resolve("file-utf8.properties");
      Files.write(cafe, "file.cafe = café au lait\nfile.plain = plain\n"
          .getBytes(StandardCharsets.UTF_8));
      JsonObject fmarker = new JsonObject();
      fmarker.addProperty("kind", "loadFile");
      w.println(fmarker.toString());
      Config.load(new File(cafe.toString()));
      for (String key : List.of("file.cafe", "file.plain")) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "file");
        o.addProperty("key", key);
        o.addProperty("value", Config.get(key));
        w.println(o.toString());
      }

      // 6. set/remove/allPropertyNames, mirroring ConfigTest.
      java.util.Set<String> snapshot = Config.allPropertyNames();
      JsonObject before = new JsonObject();
      before.addProperty("kind", "setRemove");
      before.addProperty("step", "before");
      before.addProperty("contains", snapshot.contains("bing.bong.do"));
      w.println(before.toString());
      Config.set("bing.bong.do", "true");
      JsonObject afterSet = new JsonObject();
      afterSet.addProperty("kind", "setRemove");
      afterSet.addProperty("step", "afterSet");
      afterSet.addProperty("contains", Config.allPropertyNames().contains("bing.bong.do"));
      afterSet.addProperty("value", Config.get("bing.bong.do"));
      w.println(afterSet.toString());
      Config.remove("bing.bong.do");
      JsonObject afterRemove = new JsonObject();
      afterRemove.addProperty("kind", "setRemove");
      afterRemove.addProperty("step", "afterRemove");
      afterRemove.addProperty("contains", Config.allPropertyNames().contains("bing.bong.do"));
      afterRemove.addProperty("snapshotContains", snapshot.contains("bing.bong.do"));
      w.println(afterRemove.toString());
    }
  }

  // ------------------------------------------------------------------- CSV

  private static void csvCase(PrintWriter w, String name, String input, char sep,
      boolean hasSep) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "case");
    o.addProperty("name", name);
    o.addProperty("input", input);
    if (hasSep) {
      o.addProperty("sep", String.valueOf(sep));
    } else {
      o.add("sep", JsonNull.INSTANCE);
    }
    o.add("rows", JsonNull.INSTANCE);
    List<LinkedHashMap<String, String>> rows = null;
    try {
      rows = hasSep ? SimpleCSV.parse(input, sep) : SimpleCSV.parse(input);
      o.add("parse", rowsJson(rows));
    } catch (Throwable e) {
      o.addProperty("parse", err(e));
    }
    if (rows == null) {
      o.add("unparse", JsonNull.INSTANCE);
      o.add("unparseSep", JsonNull.INSTANCE);
    } else {
      List<LinkedHashMap<String, String>> finalRows = rows;
      strOrErr(o, "unparse", () -> SimpleCSV.unparse(finalRows));
      strOrErr(o, "unparseSep", () -> SimpleCSV.unparse(finalRows, '|'));
    }
    o.addProperty("valid", SimpleCSV.isValid(input));
    o.addProperty("validSep", hasSep ? SimpleCSV.isValid(input, sep) : SimpleCSV.isValid(input));
    try {
      Iterator<LinkedHashMap<String, String>> it = SimpleCSV.parseLineByLine(input);
      List<LinkedHashMap<String, String>> collected = new ArrayList<>();
      while (it.hasNext()) {
        collected.add(it.next());
      }
      o.add("lineByLine", rowsJson(collected));
    } catch (Throwable e) {
      o.addProperty("lineByLine", err(e));
    }
    w.println(o.toString());
  }

  private static void csvDedicated(PrintWriter w, String name,
      List<LinkedHashMap<String, String>> rows) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "case");
    o.addProperty("name", name);
    o.add("input", JsonNull.INSTANCE);
    o.add("sep", JsonNull.INSTANCE);
    o.add("rows", rowsJson(rows));
    o.add("parse", JsonNull.INSTANCE);
    strOrErr(o, "unparse", () -> SimpleCSV.unparse(rows));
    strOrErr(o, "unparseSep", () -> SimpleCSV.unparse(rows, '|'));
    o.add("valid", JsonNull.INSTANCE);
    o.add("validSep", JsonNull.INSTANCE);
    o.add("lineByLine", JsonNull.INSTANCE);
    w.println(o.toString());
  }

  private static LinkedHashMap<String, String> rowOf(String... kv) {
    LinkedHashMap<String, String> row = new LinkedHashMap<>();
    for (int i = 0; i < kv.length; i += 2) {
      row.put(kv[i], kv[i + 1]);
    }
    return row;
  }

  private static void writeCsv(Path outdir) throws Exception {
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(outdir.resolve("csv.jsonl"), StandardCharsets.UTF_8))) {
      // (a) Every CSV resource under java/src/main/resources.
      Path root = Paths.get("src/main/resources");
      Map<String, Path> byRel = new LinkedHashMap<>();
      try (var stream = Files.walk(root)) {
        for (Path p : stream.filter(p -> p.toString().endsWith(".csv")).toList()) {
          String rel = root.relativize(p).toString().replace(File.separatorChar, '/');
          byRel.put(rel, p);
        }
      }
      List<String> rels = new ArrayList<>(byRel.keySet());
      rels.sort(String::compareTo);
      for (String rel : rels) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "file");
        o.addProperty("path", rel);
        String content = new String(Files.readAllBytes(byRel.get(rel)), StandardCharsets.UTF_8);
        try {
          List<LinkedHashMap<String, String>> rows = SimpleCSV.parse(content);
          o.addProperty("rows", rows.size());
          JsonArray cols = new JsonArray();
          if (!rows.isEmpty()) {
            for (String col : rows.get(0).keySet()) {
              cols.add(col);
            }
          }
          o.add("cols", cols);
          MessageDigest digest = MessageDigest.getInstance("SHA-256");
          for (LinkedHashMap<String, String> row : rows) {
            digest.update((rowJson(row).toString() + "\n").getBytes(StandardCharsets.UTF_8));
          }
          StringBuilder hex = new StringBuilder();
          for (byte b : digest.digest()) {
            hex.append(String.format("%02x", b));
          }
          o.addProperty("sha256", hex.toString());
          o.add("first", rowsJson(rows.subList(0, Math.min(3, rows.size()))));
          o.add("last", rowsJson(rows.subList(Math.max(0, rows.size() - 3), rows.size())));
        } catch (Throwable e) {
          o.addProperty("error", e.getClass().getSimpleName());
        }
        w.println(o.toString());
      }

      // (b) Tricky cases.
      String testCsv = "ID,NAME,AGE\n0,Alice,30\n1,Bob,25\n2,Charles,50\n";
      csvCase(w, "basic", testCsv, ',', false);
      csvCase(w, "basicAltSep", "ID|NAME|AGE\n0|Alice|30\n1|Bob|25\n2|Charles|50\n", '|', true);
      csvCase(w, "quotedComma", "A,B\n\"x,y\",z\n", ',', false);
      csvCase(w, "doubledQuote", "A,B\n\"x\"\"y\",z\n", ',', false);
      csvCase(w, "embeddedNewline", "A,B\n\"x\ny\",z\nw,q\n", ',', false);
      csvCase(w, "crlfInput", "A,B\r\n1,2\r\n3,4\r\n", ',', false);
      csvCase(w, "crOnlyInput", "A,B\r1,2\r3,4\r", ',', false);
      csvCase(w, "emptyValues", "A,B,C\na,,c\n", ',', false);
      csvCase(w, "trailingEmptyColumn", "A,B,C\na,b,\n", ',', false);
      csvCase(w, "quotedEmpty", "A,B\n\"\",x\n", ',', false);
      csvCase(w, "spacesAroundFields", "A,B\n  x  ,  y\n", ',', false);
      csvCase(w, "headerSpaceAfterSeparator", "A, B\n1,2\n", ',', false);
      csvCase(w, "bomPrefixed", "﻿A,B\n1,2\n", ',', false);
      csvCase(w, "headerOnly", "A,B\n", ',', false);
      csvCase(w, "headerOnlyNoNewline", "A,B", ',', false);
      csvCase(w, "emptyString", "", ',', false);
      csvCase(w, "blankHeaderLine", "\n", ',', false);
      csvCase(w, "blankLineBetweenRows", "A,B\n1,2\n\n3,4\n", ',', false);
      csvCase(w, "blankLineAtEnd", "A,B\n1,2\n\n", ',', false);
      csvCase(w, "spaceLineBetweenRows", "A,B\n \n1,2\n", ',', false);
      csvCase(w, "fewerColumns", "A,B,C\n1,2\n", ',', false);
      csvCase(w, "moreColumns", "A,B\n1,2,3\n", ',', false);
      csvCase(w, "unclosedQuote", "A,B\n\"x,y\n", ',', false);
      csvCase(w, "quoteInMiddleOfUnquoted", "A,B\na\"b,c\n", ',', false);
      csvCase(w, "onlySpacesRow", "A,B\n , \n", ',', false);
      csvCase(w, "spaceAfterQuotedField", "A,B\n\"x\" ,y\n", ',', false);
      csvCase(w, "quoteThenChars", "A,B\n\"x\"z,y\n", ',', false);
      csvCase(w, "quotedHeaderSpaces", "\" A \",\"B \"\n1,2\n", ',', false);
      csvCase(w, "headerTrailingEmptyColumn", "A,B,\n1,2,\n", ',', false);
      csvCase(w, "headerLeadingEmpty", ",B\n1,2\n", ',', false);
      csvCase(w, "duplicateHeader", "A,A\n1,2\n", ',', false);
      csvCase(w, "quotedCrlfInside", "A,B\r\n\"x\r\ny\",z\r\n", ',', false);
      csvCase(w, "afterQuoteTab", "A,B\n\"x\"\t,y\n", ',', false);
      csvCase(w, "singleQuoteValues", "A,B\n'x',y\n", ',', false);
      csvCase(w, "allEmptyRow", "A,B,C\n,,\n", ',', false);
      csvCase(w, "rowWithOnlySeparator", "A,B\n,\n", ',', false);
      csvCase(w, "extraQuotedEmptyTrailing", "A,B\n1,2,\"\"\n", ',', false);
      csvCase(w, "extraSpaceTrailing", "A,B\n1,2, \n", ',', false);
      csvCase(w, "tabSeparated", "A\tB\n1\t2\n", '\t', true);
      csvCase(w, "isValidInconsistent", "a,b,c\n1,2\nx,y,z,w\n", ',', false);
      csvCase(w, "isValidPipeData", "a|b|c\n1|2|3\n", '|', true);

      // Dedicated unparse cases (rows built directly, not parsed).
      LinkedHashMap<String, String> r1 = rowOf(
          "A", "x,y", "B", "he\"llo", "C", "line1\nline2", "D", "plain", "E", "", "G", "a!b");
      r1.put("F", null);
      LinkedHashMap<String, String> r2 = rowOf(
          "A", "a\rb", "B", " lead", "C", "trail ", "D", "\"quoted\"", "E", "x|y",
          "F", "z", "G", "a-b");
      csvDedicated(w, "unparseSpecialValues", List.of(r1, r2));
      csvDedicated(w, "unparseEmptyList", new ArrayList<>());
      csvDedicated(w, "unparseExtraKey", List.of(rowOf("A", "1"), rowOf("A", "2", "B", "3")));
    }
  }

  // ------------------------------------------------------------------- YML

  private static String className(Object value) {
    return value == null ? "null" : value.getClass().getSimpleName();
  }

  private static void ymlGet(PrintWriter w, String docName, SimpleYML doc, String path) {
    JsonObject o = new JsonObject();
    o.addProperty("kind", "get");
    o.addProperty("doc", docName);
    o.addProperty("path", path);
    try {
      Object value = doc.get(path);
      o.addProperty("class", className(value));
      o.addProperty("value", String.valueOf(value));
    } catch (Throwable e) {
      o.addProperty("error", e.getClass().getSimpleName());
    }
    w.println(o.toString());
  }

  private static void writeYml(Path outdir) throws Exception {
    try (PrintWriter w = new PrintWriter(
        Files.newBufferedWriter(outdir.resolve("yml.jsonl"), StandardCharsets.UTF_8))) {
      String synthetic =
          "plain_int: 42\n"
          + "neg_int: -7\n"
          + "long_int: 3000000000\n"
          + "big_int: 123456789012345678901234567890\n"
          + "float_val: 1.5\n"
          + "exp_float: 1.0e+3\n"
          + "exp_float_unsigned: 1.0e3\n"
          + "plain_exp_float: 1e3\n"
          + "bool_true: true\n"
          + "bool_false: false\n"
          + "yes_val: yes\n"
          + "no_val: no\n"
          + "on_val: on\n"
          + "off_val: off\n"
          + "null_val: null\n"
          + "tilde_val: ~\n"
          + "empty_val:\n"
          + "plain_str: hello world\n"
          + "single_quoted: 'yes'\n"
          + "double_quoted: \"1.5\"\n"
          + "date_val: 2026-01-15\n"
          + "octal_val: 012\n"
          + "hex_val: 0x1F\n"
          + "binary_val: 0b101\n"
          + "zero_o_str: 0o17\n"
          + "sexagesimal_val: 1:20\n"
          + "inf_val: .inf\n"
          + "flow_list: [1.0, 2.0]\n"
          + "block_list:\n  - alpha\n  - beta\n"
          + "nested:\n  inner: 5\n  deep:\n    leaf: deep value\n";
      Files.writeString(outdir.resolve("synthetic.yml"), synthetic, StandardCharsets.UTF_8);
      Object loaded = new Yaml().load(synthetic);
      @SuppressWarnings("unchecked")
      Map<String, Object> map = (Map<String, Object>) loaded;
      for (Map.Entry<String, Object> e : map.entrySet()) {
        JsonObject o = new JsonObject();
        o.addProperty("kind", "scalar");
        o.addProperty("key", e.getKey());
        o.addProperty("class", className(e.getValue()));
        o.addProperty("value", String.valueOf(e.getValue()));
        w.println(o.toString());
      }

      // get() paths on the SimpleYML javadoc example.
      SimpleYML nested = new SimpleYML(
          "foo:\n  bar: 2\n  baz: 4\n  qux:\n    corge: 9\n    grault: -1\nplugh: 7\n");
      for (String path : List.of(
          "foo.bar", "foo.baz", "foo.qux.grault", "foo.qux.corge", "plugh", "foo",
          "foo.missing", "missing", "missing.deep", "foo.bar.deep", "foo.missing.deep")) {
        ymlGet(w, "nested", nested, path);
      }
      SimpleYML empty = new SimpleYML("");
      ymlGet(w, "empty", empty, "x");
      ymlGet(w, "empty", empty, "x.y");

      // A non-map document fails the constructor's cast to Map.
      JsonObject co = new JsonObject();
      co.addProperty("kind", "construct");
      co.addProperty("name", "listTop");
      try {
        new SimpleYML("- a\n- b\n");
        co.addProperty("error", "NONE");
      } catch (Throwable e) {
        co.addProperty("error", e.getClass().getSimpleName());
      }
      w.println(co.toString());

      // get() on the real resources.
      String[][] resourceGets = {
          {"biometrics.yml", "lifecycle.prevalence_of_twins"},
          {"biometrics.yml", "lifecycle.adult_weight_gain"},
          {"biometrics.yml", "metabolic.blood_pressure.normal.systolic"},
          {"biometrics.yml", "metabolic.basic_panel.normal.sodium"},
          {"names.yml", "street.secondary"},
          {"names.yml", "street.type"},
      };
      for (String[] rg : resourceGets) {
        String content = Files.readString(
            Paths.get("src/main/resources", rg[0]), StandardCharsets.UTF_8);
        SimpleYML doc = new SimpleYML(content);
        JsonObject o = new JsonObject();
        o.addProperty("kind", "resourceGet");
        o.addProperty("file", rg[0]);
        o.addProperty("path", rg[1]);
        try {
          Object value = doc.get(rg[1]);
          o.addProperty("class", className(value));
          o.addProperty("value", String.valueOf(value));
        } catch (Throwable e) {
          o.addProperty("error", e.getClass().getSimpleName());
        }
        w.println(o.toString());
      }
    }
  }
}
