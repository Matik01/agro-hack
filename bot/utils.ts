import {Context} from "grammy";
const axios = require('axios');

export const botAnswer =  async (ctx: Context) => {
    const data = {
        id: new Date().toDateString(),
        message: ctx.message?.text
    }

    return await axios.post(process.env.API_URL, data)
        .then(response => {
            console.log(response.data);
        })
        .catch(error => {
            console.error(error);
        });
}
