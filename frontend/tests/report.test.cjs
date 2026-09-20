const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');

test('inspection export is standalone, readable, and escapes model text', async () => {
  let captured, clicked = false;
  const context = {exports:{}, Blob, URL:{createObjectURL(blob){captured=blob;return 'blob:test'},revokeObjectURL(){}},
    document:{createElement(){return {click(){clicked=true}}}},setTimeout(){}};
  const code=ts.transpileModule(fs.readFileSync('lib/report.ts','utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS}}).outputText;
  vm.runInNewContext(code,context);
  context.exports.downloadInspectionReport({exported_at:'2026-09-20T12:00:00Z',domain:'agriculture',provider:'anthropic',model:'test',
    synthetic:false,image:null,observations:'<script>unsafe</script>',regions:null,review:null,metrics:null,
    finding:{primary_finding:'Review leaf',review_status:'needs_review',recommended_action:'Inspect in field',evidence_chain:[],limitations:['Approximate region']}});
  assert.equal(clicked,true);
  const html=await captured.text();
  assert.ok(html.includes('NEEDS HUMAN REVIEW'));
  assert.ok(html.includes('Inspect in field'));
  assert.ok(html.includes('&lt;script&gt;unsafe&lt;/script&gt;'));
  assert.ok(!html.includes('<script>'));
});
