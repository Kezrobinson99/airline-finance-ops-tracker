import React,{useEffect,useState} from "react";
import {apiGet,apiPost,money} from "../api";

export default function BuyPage(){
  const [airlines,setAirlines]=useState([]);
  const [selectedAirline,setSelectedAirline]=useState("");
  const [hubMarket,setHubMarket]=useState([]);
  const [routes,setRoutes]=useState([]);
  const [aircraft,setAircraft]=useState([]);
  const [purchases,setPurchases]=useState([]);
  const [customRoute,setCustomRoute]=useState("MAN - JFK");
  const [pricedRoute,setPricedRoute]=useState(null);

  async function load(){
    const [al,r,a,p]=await Promise.all([
      apiGet("/airlines"),
      apiGet("/routes"),
      apiGet("/aircraft"),
      apiGet("/purchases")
    ]);
    setAirlines(al);
    setRoutes(r);
    setAircraft(a);
    setPurchases(p);

    const first = selectedAirline || al[0]?.id || "";
    if(first){
      setSelectedAirline(String(first));
      await loadHubMarket(first);
    }
  }

  async function loadHubMarket(airlineId){
    try {
      const hubs = await apiGet(`/hub-market/${airlineId}`);
      setHubMarket(hubs);
    } catch {
      const allHubs = await apiGet("/hubs");
      const owned = allHubs.filter(h => String(h.airline_id) === String(airlineId) && h.owned).map(h => h.airport);
      setHubMarket(allHubs.filter(h => !owned.includes(h.airport)));
    }
  }

  useEffect(()=>{load()},[]);

  async function changeAirline(id){
    setSelectedAirline(id);
    await loadHubMarket(id);
  }

  async function buy(item_type,item_name,cost,notes="Purchased from sim marketplace"){
    await apiPost("/purchases",{
      airline_id:Number(selectedAirline),
      item_type,
      item_name,
      cost:Number(cost),
      notes
    });
    await load();
  }

  function priceCustomRoute(){
    const clean = customRoute.replace("–","-").toUpperCase();
    const parts = clean.split("-").map(x=>x.trim()).filter(Boolean);
    if(parts.length !== 2){
      alert("Use format like MAN - JFK");
      return;
    }

    const [origin,destination] = parts;
    const longHaul = ["JFK","MCO","TPA","LAS","IAH","SIN","DXB","YYZ","BOS","ORD","DFW"].includes(destination) || ["JFK","MCO","TPA","LAS","IAH","SIN","DXB","YYZ","BOS","ORD","DFW"].includes(origin);
    const base = longHaul ? 28000000 : 3500000;
    const premium = origin === "LHR" || destination === "LHR" ? 14000000 : 0;
    const estimated = base + premium;

    setPricedRoute({
      origin,
      destination,
      routeName:`${origin}-${destination}`,
      price: estimated,
      suggestedAircraft: longHaul ? "A330-900 / A350-1000" : "A321neo / 737 MAX",
      notes: longHaul ? "Long-haul or major trunk route priced as strategic route rights." : "Short/medium-haul route priced as regional route rights."
    });
  }

  const selectedName = airlines.find(a=>String(a.id)===String(selectedAirline))?.name || "Selected airline";

  return <>
    <div className="header">
      <div>
        <h1>Buy Aircraft, Hubs & Routes</h1>
        <p>Select an airline first. Hub market hides hubs that airline already owns.</p>
      </div>
    </div>

    <div className="panel form">
      <label>Selected Airline
        <select value={selectedAirline} onChange={e=>changeAirline(e.target.value)}>
          {airlines.map(a=><option key={a.id} value={a.id}>{a.code} · {a.name}</option>)}
        </select>
      </label>
      <p className="muted">Current market view for: <b>{selectedName}</b></p>
    </div>

    <section className="grid3">
      <div className="panel">
        <h2>Hub Market</h2>
        <p className="muted">Only hubs not already owned by this airline are shown.</p>
        {hubMarket.map(h=>
          <div className="buy" key={`${h.airport}-${h.id}`}>
            <div>
              <b>{h.airport}</b>
              <span>{h.notes} · {money(h.purchase_price)}</span>
            </div>
            <button onClick={()=>buy("Hub",h.airport,h.purchase_price,`Bought hub ${h.airport}`)}>Buy</button>
          </div>
        )}
        {hubMarket.length === 0 && <p className="muted">No hubs available for this airline.</p>}
      </div>

      <div className="panel">
        <h2>Custom Route Rights</h2>
        <p className="muted">Type a route like MAN - JFK, price it, then buy it.</p>
        <div className="form">
          <label>Route
            <input value={customRoute} onChange={e=>setCustomRoute(e.target.value)} placeholder="MAN - JFK" />
          </label>
          <button onClick={priceCustomRoute}>Price Route</button>
        </div>

        {pricedRoute && <div className="calc">
          <h3>{pricedRoute.routeName}</h3>
          <p>Suggested aircraft: <b>{pricedRoute.suggestedAircraft}</b></p>
          <p>{pricedRoute.notes}</p>
          <h2>{money(pricedRoute.price)}</h2>
          <button onClick={()=>buy("Route",pricedRoute.routeName,pricedRoute.price,`Custom route rights. Suggested aircraft: ${pricedRoute.suggestedAircraft}`)}>Buy Route</button>
        </div>}
      </div>

      <div className="panel">
        <h2>Aircraft Market</h2>
        {aircraft.map(a=>
          <div className="buy" key={a.id}>
            <div>
              <b>{a.aircraft_type}</b>
              <span>{a.registration} · {money(a.purchase_price)}</span>
            </div>
            <button onClick={()=>buy("Aircraft",a.aircraft_type,a.purchase_price)}>Buy</button>
          </div>
        )}
      </div>
    </section>

    <div className="panel">
      <h2>Purchase History</h2>
      <table>
        <thead><tr><th>Date</th><th>Type</th><th>Name</th><th>Cost</th><th>Notes</th></tr></thead>
        <tbody>{purchases.map(p=>
          <tr key={p.id}>
            <td>{p.date}</td>
            <td>{p.item_type}</td>
            <td>{p.item_name}</td>
            <td>{money(p.cost)}</td>
            <td>{p.notes}</td>
          </tr>
        )}</tbody>
      </table>
    </div>
  </>
}
