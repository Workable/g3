# flake8: noqa
def node_sample():
    return {
        "message": "Handle cv-parser new error format SRC-1426",
        "code": """
        diff --git a/src/app/services/flows/components/ConvertExtractAndCVParserParse.ts b/src/app/services/flows/
        components/ConvertExtractAndCVParserParse.ts
        index 010ff4d9..ccc999c4 100644
        --- a/src/app/services/flows/components/ConvertExtractAndCVParserParse.ts
        +++ b/src/app/services/flows/components/ConvertExtractAndCVParserParse.ts
        @@ -28,7 +28,7 @@ export default async function convertExtractParse(
        
           // Avoid continuing in CV Parser cannot find any candidate attribute
           const output = await ctx.cvParser.parse(document);
        -  if (invalidResume(output)) {
        +  if (isInValidResume(output)) {
             return error(false, false, true);
           }
        
        @@ -42,6 +42,9 @@ export default async function convertExtractParse(
           return output;
         }
        
        +function isInValidResume(resume: Candidate | { error: string }): resume is { error: string } {
        +  return invalidResume(resume);
        +}
         /**
          *
          * Steps
        @@ -52,7 +55,7 @@ export async function extractAndParse(
           input: Attachment,
           ctx: FlowContext,
           verbose = false
        -): Promise<CandidateResume | Candidate> {
        +): Promise<CandidateResume | Candidate | { error: string }> {
           if (!isResume(input)) {
             return;
           }
        diff --git a/src/app/services/rpc/CVParserBridge.ts b/src/app/services/rpc/CVParserBridge.ts
        index 58d6c60d..e2ad3cdd 100644
        --- a/src/app/services/rpc/CVParserBridge.ts
        +++ b/src/app/services/rpc/CVParserBridge.ts
        @@ -7,16 +7,22 @@ export default class CVParserBridge extends BaseBridge {
        
           protected client: CVParserClient;
        
        -  async parse(doc: DocumentContent): Promise<Candidate> {
        -    const response = await this.client.parse(request(doc));
        -
        -    return (deprecated(response) ? response.body || response.headers : response) as Candidate;
        +  async parse(doc: DocumentContent): Promise<Candidate | { error: string }> {
        +    try {
        +      const response = await this.client.parse(request(doc));
        +      return (deprecated(response) ? response.body || response.headers : response) as Candidate;
        +    } catch (e) {
        +      return { error: e.message };
        +    }
           }
        
        -  async parseVerbose(doc: DocumentContent): Promise<CandidateResume> {
        -    const response = await this.client.parse(request(doc, true));
        -
        -    return (deprecated(response) ? response.body || response.headers : response) as CandidateResume;
        +  async parseVerbose(doc: DocumentContent): Promise<CandidateResume | { error: string }> {
        +    try {
        +      const response = await this.client.parse(request(doc, true));
        +      return (deprecated(response) ? response.body || response.headers : response) as CandidateResume;
        +    } catch (e) {
        +      return { error: e.message };
        +    }
           }
         }
        
        diff --git a/src/test/helpers.ts b/src/test/helpers.ts
        index 2aee833f..b707f498 100644
        --- a/src/test/helpers.ts
        +++ b/src/test/helpers.ts
        @@ -157,7 +157,12 @@ export function walkTheBridge(
             bridgeInput = [<any>{ version: '1', meta: { source: 'test' } }],
             clientOutput = <any>{ output: true },
             bridgeOutput = <any>{ output: true },
        -    clientCalled = true
        +    clientCalled = true,
        +    rabbitMethod = 'getTopicReply',
        +    rabbitInput = [],
        +    rabbitOutput = {},
        +    stubRabbit = false,
        +    testErrors = !stubRabbit
           } = {}
         ) {
           return async function(bridge = this.bridge) {
        @@ -165,10 +170,19 @@ export function walkTheBridge(
               bridge.client[clientMethod].callCount.should.equal(0);
               return;
             }
        -    const scenario = composeScenario([
        -      { spy: bridge.client[clientMethod], input: clientInput, output: clientOutput },
        -      { spy: bridge.client[clientMethod], input: clientInput, output: new Error('Bridge Error') }
        -    ]);
        +    let scenario;
        +    if (stubRabbit) {
        +      scenario = composeScenario([
        +        { spy: Rabbit[rabbitMethod], input: rabbitInput, op: 'containDeep', output: rabbitOutput }
        +      ]);
        +    } else {
        +      scenario = composeScenario([
        +        { spy: bridge.client[clientMethod], input: clientInput, output: clientOutput },
        +        ...(testErrors
        +          ? [{ spy: bridge.client[clientMethod], input: clientInput, output: new Error('Bridge Error') }]
        +          : [])
        +      ]);
        +    }
        
             if (!bridgeOutput) {
               should.equal(bridgeOutput, await bridge[methodName](...bridgeInput));
        @@ -176,11 +190,13 @@ export function walkTheBridge(
               bridgeOutput.should.eql(await bridge[methodName](...bridgeInput));
             }
        
        -    try {
        -      await bridge[methodName](...bridgeInput);
        -      throw new Error('Missing exception');
        -    } catch (err) {
        -      'Bridge Error'.should.eql(err.message);
        +    if (testErrors) {
        +      try {
        +        await bridge[methodName](...bridgeInput);
        +        throw new Error('Missing exception');
        +      } catch (err) {
        +        'Bridge Error'.should.eql(err.message);
        +      }
             }
        
             scenario.verify();
        diff --git a/src/test/services/rpc/CVParserBridgeTest.ts b/src/test/services/rpc/CVParserBridgeTest.ts
        index 014a776c..8538e87c 100644
        --- a/src/test/services/rpc/CVParserBridgeTest.ts
        +++ b/src/test/services/rpc/CVParserBridgeTest.ts
        @@ -16,6 +16,10 @@ describe('CVParserBridge', function() {
             parsedResume = this.fx.parseOnlyFlow.parsedResume;
           });
        
        +  afterEach(function() {
        +    this.sandbox.restore();
        +  });
        +
           // Parse (consumed by ATS, Referrals, Application form and Profile form )
           describe('parse', function() {
             context('when parsable document provided', function() {
        @@ -24,7 +28,8 @@ describe('CVParserBridge', function() {
                   bridgeInput: document(),
                   clientInput: document().map(doc => ({ ...doc, extended_output: false })),
                   clientOutput: parsedCandidate,
        -          bridgeOutput: parsedCandidate
        +          bridgeOutput: parsedCandidate,
        +          testErrors: false
                 });
                 await test(this.bridge);
               });
        @@ -32,10 +37,19 @@ describe('CVParserBridge', function() {
        
             context('when parsable document provided to legacy parser', function() {
               it('calls the client with extended_output false', async function() {
        +        this.bridge = new CVParserBridge(<FlowProps>{});
        +        this.sandbox.stub(Rabbit, 'getTopicReply');
        +
                 const test = walkTheBridge('parse', {
                   bridgeInput: document(),
        -          clientInput: document().map(doc => ({ ...doc, extended_output: false })),
        -          clientOutput: { body: parsedCandidate },
        +          stubRabbit: true,
        +          rabbitInput: [
        +            'parse_v2',
        +            ...document().map(doc => ({ ...doc, extended_output: false })),
        +            { headers: { replayed: false } },
        +            undefined
        +          ],
        +          rabbitOutput: { body: parsedCandidate },
                   bridgeOutput: parsedCandidate
                 });
                 await test(this.bridge);
        @@ -48,7 +62,26 @@ describe('CVParserBridge', function() {
                   bridgeInput: document(),
                   clientInput: document().map(doc => ({ ...doc, extended_output: false })),
                   clientOutput: { error: 'RuntimeError: Length of text exceeded threshold' },
        -          bridgeOutput: { error: 'RuntimeError: Length of text exceeded threshold' }
        +          bridgeOutput: { error: 'RuntimeError: Length of text exceeded threshold' },
        +          testErrors: false
        +        });
        +        await test(this.bridge);
        +      });
        +
        +      it('calls the client with extended_output false and output headers error', async function() {
        +        this.bridge = new CVParserBridge(<FlowProps>{});
        +        this.sandbox.stub(Rabbit, 'getTopicReply');
        +        const test = walkTheBridge('parse', {
        +          bridgeInput: document(),
        +          stubRabbit: true,
        +          rabbitInput: [
        +            'parse_v2',
        +            ...document().map(doc => ({ ...doc, extended_output: false })),
        +            { headers: { replayed: false } },
        +            undefined
        +          ],
        +          rabbitOutput: { headers: { error: 'RuntimeError: Length of text exceeded threshold' } },
        +          bridgeOutput: { error: '[cvparser->parse_v2] RuntimeError: Length of text exceeded threshold' }
                 });
                 await test(this.bridge);
               });
        @@ -60,7 +93,8 @@ describe('CVParserBridge', function() {
                   bridgeInput: document(),
                   clientInput: document().map(doc => ({ ...doc, extended_output: false })),
                   clientOutput: { headers: { error: 'RuntimeError: Length of text exceeded threshold' } },
        -          bridgeOutput: { error: 'RuntimeError: Length of text exceeded threshold' }
        +          bridgeOutput: { error: 'RuntimeError: Length of text exceeded threshold' },
        +          testErrors: false
                 });
                 await test(this.bridge);
               });
        @@ -76,7 +110,8 @@ describe('CVParserBridge', function() {
                   bridgeInput: document(),
                   clientInput: document().map(doc => ({ ...doc, extended_output: true })),
                   clientOutput: parsedResume,
        -          bridgeOutput: parsedResume
        +          bridgeOutput: parsedResume,
        +          testErrors: false
                 });
        
                 await test(this.bridge);
        @@ -90,12 +125,32 @@ describe('CVParserBridge', function() {
                   bridgeInput: document(),
                   clientInput: document().map(doc => ({ ...doc, extended_output: true })),
                   clientOutput: { body: parsedResume },
        -          bridgeOutput: parsedResume
        +          bridgeOutput: parsedResume,
        +          testErrors: false
                 });
        
                 await test(this.bridge);
               });
             });
        +
        +    context('when invalid document provided', function() {
        +      it('calls the client with extended_output true and output headers error', async function() {
        +        this.bridge = new CVParserBridge(<FlowProps>{});
        +        this.sandbox.stub(Rabbit, 'getTopicReply');
        +        const test = walkTheBridge('parseVerbose', {
        +          bridgeInput: document(),
        +          stubRabbit: true,
        +          rabbitInput: [
        +            'parse_v2',
        +            ...document().map(doc => ({ ...doc, extended_output: true })),
        +            { headers: { replayed: false } }
        +          ],
        +          rabbitOutput: { headers: { error: 'RuntimeError: Length of text exceeded threshold' } },
        +          bridgeOutput: { error: '[cvparser->parse_v2] RuntimeError: Length of text exceeded threshold' }
        +        });
        +        await test(this.bridge);
        +      });
        +    });
           });
         });
        """,
    }
