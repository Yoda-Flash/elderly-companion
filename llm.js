import {parseArgs} from 'node:util';
import 'readline';
import * as readline from "node:readline";
import * as winston from 'winston';

const logger = winston.createLogger({
    level: 'debug',
    format: winston.format.simple(),
    transports: [
        new winston.transports.File({filename: 'llm.log'}),
    ],
});

class LLM {
    constructor() {
        this.prompted = false;
    }

    prompt_running = async () => {
        while (this.prompted) {
            await new Promise(resolve => setTimeout(resolve, 2000));
        }
    }

    format_prompt = (prompt) => {
        return `<|begin_of_text|><|start_header_id|>user<|end_header_id|> \n ${prompt} <|eot_id|> \n <|start_header_id|>assistant<|end_header_id|>`;
    }

    chat = async (prompt, tokens) => {
        this.prompted = true;
        let response = await fetch("https://ai.hackclub.com/chat/completions", {
        // let response = await fetch("http://host.docker.internal:8080/completion", {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "messages": [{
                    "role": "user",
                    "content": prompt
                }],
                // stream: true
            })
        })

        const reader = response.body.getReader()
        const decoder = new TextDecoder("utf-8", {ignoreBOM: true})
        let partialData = '';
        let parsedData = '';

        while (true) {
            const {done, value} = await reader.read();
            if (done) break;

            partialData = decoder.decode(value, {stream: true});
            try {
                // parsedData = JSON.parse(JSON.parse(JSON.stringify(partialData))).choices[0].delta.content;
                parsedData = JSON.parse(JSON.parse(JSON.stringify(partialData))).choices[0].message.content;
                process.stdout.write(parsedData)
                // if (parsedData.includes(".")) {
                //     let sentences = parsedData.split('.');
                //     console.log(sentences);
                //     for (var i = 0; i < sentences.length; i++){
                //         process.stdout.write("\n");
                //         // process.stderr.write("\n");
                //     }
                // } else {
                //     process.stdout.write(parsedData);
                //     logger.info(`Response: ${parsedData}`)
                    // process.stderr.write(parsedData);
                // }
            } catch {
                continue
            }
        }

        process.stdout.write("\n");
        this.prompted = false;
    }
}

async function main(){
    const llm = new LLM();

    const argOptions = {
        prompt: {type: 'string', short: 'p', default: ''},
        tokens: {type: 'string', short: 't', default: '200'},
        mode: {type: 'string', short: 'm', default: 'local'}
    }
    const args = parseArgs({options: argOptions});
    logger.info(`Starting llm with: ${args}`);

    if (args.values.prompt !== ''){
        llm.chat(args.values.prompt, parseInt(args.values.tokens)).catch(err => console.log(err));
        await llm.prompt_running();
        process.exit(0);
    }

    let running = true;
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    })
    while (running) {
        rl.question("", (prompt) => {
            logger.info(`Prompt: ${prompt}`);
            if (prompt === "stop") {
                running = false;
                llm.prompted = false;
                return;
            }
            llm.chat(prompt, args.values.tokens).catch(err => console.log(err));
        });
        llm.prompted = true;
        await llm.prompt_running();
    }
    process.exit(0);

}

main().catch(err => console.log(err));