import {Context} from "grammy";
import {botAnswer} from "./utils";
require('dotenv').config()

const {Bot} = require('grammy')

const bot = new Bot(process.env.BOT_API_KEY)

bot
    .on('msg')
    .filter((ctx: Context) => !!ctx.message?.text?.toLowerCase(), botAnswer)

bot.start()

