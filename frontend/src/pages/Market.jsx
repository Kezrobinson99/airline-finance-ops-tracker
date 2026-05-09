
import React,{useEffect,useState}from'react';import{apiGet,apiPost,money}from'../api';

export default function Market(){
  const[air,setAir]=useState([]),[p,setP]=useState([]),[hubMarket,setHubMarket]=useState([]);
  const[airline,setAirline]=useState(1);
  const[routeInput,setRouteInput]=useState('MAN - JFK');
  const[quote,setQuote]=useState(null);
  const[routeForm,setRouteForm]=useState({aircraft_type:'A330-900',economy_price:390,premium_price:780,business_price:2400,flight_number:'',return_flight_number:''});
  const[msg,setMsg]=useState('');

  async function load(selected=airline){
    const airlines=await apiGet('/airlines');setAir(airlines);
    const id=selected || airlines[0]?.id || 1;
    setP(await apiGet('/purchases'));
    setHubMarket(await apiGet(`/hub-market?airline_id=${id}`));
  }
  useEffect(()=>{load()},[]);

  async function changeAirline(id){setAirline(Number(id));setQuote(null);await load(Number(id));}

  async function buyAircraft(t,c,b){
    await apiPost('/buy/aircraft',{airline_id:Number(airline),registration:`SIM-${Math.floor(Math.random()*9000)}`,aircraft_type:t,purchase_price:c,fuel_burn_per_hour:b});
    setMsg(`Bought ${t}`);load();
  }

  async function buyHub(option){
    await apiPost('/buy/hub-market',{airline_id:Number(airline),airport:option.airport});
    setMsg(`Bought ${option.airport} hub for ${money(option.purchase_cost)}`);load();
  }

  function splitRoute(){
    const cleaned=routeInput.toUpperCase().replace(' TO ','-').replace('–','-');
    const parts=cleaned.split('-').map(x=>x.trim()).filter(Boolean);
    return {origin:parts[0]||'',destination:parts[1]||''};
  }

  async function priceRoute(){
    const r=splitRoute();
    if(!r.origin || !r.destination){setMsg('Type a route like MAN - JFK');return;}
    const q=await apiPost('/route/quote',{airline_id:Number(airline),origin:r.origin,destination:r.destination});
    setQuote(q);
    setRouteForm({
      aircraft_type:q.suggested_aircraft,
      economy_price:q.suggested_economy_price,
      premium_price:q.suggested_premium_price,
      business_price:q.suggested_business_price,
      flight_number:`${q.airline_code}${Math.floor(100+Math.random()*800)}`,
      return_flight_number:`${q.airline_code}${Math.floor(900+Math.random()*90)}`
    });
    setMsg(`Priced ${q.origin}-${q.destination} at ${money(q.route_purchase_cost)}`);
  }

  async function buyCustomRoute(){
    const r=splitRoute();
    const bought=await apiPost('/buy/custom-route',{
      airline_id:Number(airline),
      origin:r.origin,
      destination:r.destination,
      aircraft_type:routeForm.aircraft_type,
      economy_price:Number(routeForm.economy_price),
      premium_price:Number(routeForm.premium_price),
      business_price:Number(routeForm.business_price),
      flight_number:routeForm.flight_number,
      return_flight_number:routeForm.return_flight_number
    });
    setMsg(`Bought route ${r.origin}-${r.destination}. Now go to Routes and assign aircraft if needed.`);
    await load();
  }

  return <>
    <div className="head"><div><h1>Buy Aircraft, Hubs & Routes</h1><p>Select Regal or Monarch, buy new hubs you do not own, or type any route and price it.</p></div></div>

    {msg&&<div className="panel ok">{msg}</div>}

    <div className="panel"><label>Buying for
      <select value={airline} onChange={e=>changeAirline(e.target.value)}>
        {air.map(a=><option key={a.id} value={a.id}>{a.code} {a.name}</option>)}
      </select>
    </label></div>

    <div className="grid3">
      <div className="panel"><h2>Aircraft Market</h2>
        <button onClick={()=>buyAircraft('A321neo',54000000,2450)}>Buy A321neo · {money(54000000)}</button>
        <button onClick={()=>buyAircraft('737 MAX 8',50000000,2350)}>Buy 737 MAX 8 · {money(50000000)}</button>
        <button onClick={()=>buyAircraft('A330-900',112000000,5400)}>Buy A330-900 · {money(112000000)}</button>
        <button onClick={()=>buyAircraft('A350-1000',155000000,6800)}>Buy A350-1000 · {money(155000000)}</button>
      </div>

      <div className="panel"><h2>Hub Market</h2>
        <p className="muted">Only shows hubs this airline does not already own.</p>
        {hubMarket.length===0&&<p className="muted">No new hubs available for this airline.</p>}
        {hubMarket.map(h=><div className="marketCard" key={h.airport}>
          <b>{h.airport} · {h.name}</b>
          <span>{h.notes}</span>
          <strong>{money(h.purchase_cost)}</strong>
          <button onClick={()=>buyHub(h)}>Buy Hub</button>
        </div>)}
      </div>

      <div className="panel"><h2>Custom Route Purchase</h2>
        <label>Route<input value={routeInput} onChange={e=>setRouteInput(e.target.value)} placeholder="MAN - JFK"/></label>
        <button onClick={priceRoute}>Price Route</button>
        {quote&&<div className="quoteBox">
          <h3>{quote.origin}-{quote.destination}</h3>
          <p>Distance: <b>{quote.distance_nm}nm</b></p>
          <p>Suggested aircraft: <b>{quote.suggested_aircraft}</b></p>
          <p>Route rights price: <b>{money(quote.route_purchase_cost)}</b></p>
          <label>Flight No<input value={routeForm.flight_number} onChange={e=>setRouteForm({...routeForm,flight_number:e.target.value})}/></label>
          <label>Return No<input value={routeForm.return_flight_number} onChange={e=>setRouteForm({...routeForm,return_flight_number:e.target.value})}/></label>
          <label>Aircraft Type<select value={routeForm.aircraft_type} onChange={e=>setRouteForm({...routeForm,aircraft_type:e.target.value})}>
            {['A321neo','737 MAX 8','A330-900','A350-1000','A340-600'].map(x=><option key={x}>{x}</option>)}
          </select></label>
          <div className="miniGrid">
            <label>Economy<input type="number" value={routeForm.economy_price} onChange={e=>setRouteForm({...routeForm,economy_price:e.target.value})}/></label>
            <label>Premium<input type="number" value={routeForm.premium_price} onChange={e=>setRouteForm({...routeForm,premium_price:e.target.value})}/></label>
            <label>Business<input type="number" value={routeForm.business_price} onChange={e=>setRouteForm({...routeForm,business_price:e.target.value})}/></label>
          </div>
          <button onClick={buyCustomRoute}>Buy This Route</button>
        </div>}
      </div>
    </div>

    <div className="panel"><h2>Purchase History</h2><table><tbody>{p.map(x=><tr key={x.id}><td>{x.date}</td><td>{x.item_type}</td><td>{x.item_name}</td><td>{money(x.cost)}</td></tr>)}</tbody></table></div>
  </>
}
