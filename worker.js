const reply=(data,status=200)=>Response.json(data,{status,headers:{"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}});
export default {async fetch(request,env){
 const url=new URL(request.url);
 if(url.pathname!=="/api/quote")return env.ASSETS.fetch(request);
 if(request.method!=="POST")return reply({ok:false},405);
 if(request.headers.get("Origin")!==url.origin||!request.headers.get("Content-Type")?.startsWith("application/json"))return reply({ok:false},403);
 if(!env.RESEND_API_KEY||!env.QUOTE_FROM)return reply({ok:false,error:"Envio automático ainda não configurado."},503);
 const limit=await env.QUOTE_LIMIT.limit({key:request.headers.get("CF-Connecting-IP")||"unknown"});
 if(!limit.success)return reply({ok:false,error:"Aguarde antes de tentar novamente."},429);
 try{
 const raw=await request.text();if(raw.length>12000)return reply({ok:false},413);
 const {message,email}=JSON.parse(raw);
 if(typeof message!=="string"||message.length<20||message.length>6500||typeof email!=="string"||email.length>160||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return reply({ok:false,error:"Confira os dados."},400);
 const res=await fetch("https://api.resend.com/emails",{method:"POST",headers:{Authorization:"Bearer "+env.RESEND_API_KEY,"Content-Type":"application/json"},body:JSON.stringify({from:env.QUOTE_FROM,to:["webcoredigital@outlook.com"],reply_to:email,subject:"Novo orçamento | WebCore",text:message})});
 return res.ok?reply({ok:true}):reply({ok:false,error:"Não foi possível enviar o e-mail."},502);
 }catch{return reply({ok:false,error:"Não foi possível enviar o e-mail."},502);}
}};