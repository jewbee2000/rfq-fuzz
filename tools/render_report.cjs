// Browser-only verification of our authored offline report. No remote requests.
const fs = require('fs');
const path = require('path');
const {pathToFileURL} = require('url');
const {chromium} = require(process.env.RFQFUZZ_PLAYWRIGHT || 'playwright');
(async()=>{
  const report=path.resolve(process.argv[2]);
  const output=path.resolve(process.argv[3]);
  fs.mkdirSync(output,{recursive:true});
  const browser=await chromium.launch({headless:true,...(process.env.RFQFUZZ_BROWSER_PATH?{executablePath:process.env.RFQFUZZ_BROWSER_PATH}:{channel:'msedge'})});
  const page=await browser.newPage({viewport:{width:1360,height:900}});
  const errors=[];const requests=[];
  page.on('pageerror',error=>errors.push(String(error)));
  page.on('request',request=>requests.push(request.url()));
  await page.goto(pathToFileURL(report).href,{waitUntil:'load'});
  await page.screenshot({path:path.join(output,'report-top.png')});
  const anchors=await page.locator('a[href^="#"]').count();
  if(anchors){await page.locator('a[href^="#"]').first().click();await page.screenshot({path:path.join(output,'report-changed-evidence.png')});}
  const result={title:await page.title(),headings:await page.locator('h1').allTextContents(),anchors,errors,remoteRequests:requests.filter(url=>/^https?:/.test(url)),horizontalOverflow:await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth)};
  fs.writeFileSync(path.join(output,'browser-audit.json'),JSON.stringify(result,null,2));
  await browser.close();
  if(errors.length||result.remoteRequests.length||result.horizontalOverflow)throw new Error('offline report browser check failed');
  console.log(JSON.stringify(result));
})().catch(error=>{console.error(error);process.exitCode=1});
