
import React,{useEffect,useState}from'react';import{apiGet,apiPost,money}from'../api';

export default function Routes(){
  const[r,setR]=useState([]),[filter,setFilter]=useState('All'),[editing,setEditing]=useState(null),[newType,setNewType]=useState('A350-1000');
  async function load(){setR(await apiGet('/routes'))}
  useEffect(()=>{load()},[]);

  const shown=r.filter(x=>filter==='All'||x.airline_name?.includes(filter)||x.airline_name?.includes(filter==='Regal'?'Regal':'Monarch'));

  async function saveAircraft(route){
    await apiPost(`/routes/${route.id}/aircraft`,{aircraft_type:newType},'PATCH');
  }

  async function patchAircraft(route){
    const res=await fetch(`http://127.0.0.1:8000/routes/${route.id}/aircraft`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({aircraft_type:newType})});
    if(!res.ok){alert(await res.text());return;}
    setEditing(null);await load();
  }

  return <>
    <div className="head"><div><h1>Route Management</h1><p>All owned routes. After buying MAN-JFK, assign the aircraft type here.</p></div></div>
    <div className="panel">
      <label>Airline filter <select value={filter} onChange={e=>setFilter(e.target.value)}><option>All</option><option>Monarch</option><option>Regal</option><option>Lauda</option><option>Cargo</option></select></label>
    </div>
    <div className="panel"><table><thead><tr><th>Airline</th><th>Flight</th><th>Route</th><th>Aircraft</th><th>Distance</th><th>Revenue</th><th>Cost</th><th>Profit</th><th>Setup</th></tr></thead><tbody>
    {shown.map(x=><tr key={x.id}>
      <td>{x.airline_name}</td><td><b>{x.flight_number}/{x.return_flight_number}</b></td><td>{x.origin}-{x.destination}</td>
      <td>{editing===x.id?<select value={newType} onChange={e=>setNewType(e.target.value)}>{['A321neo','737 MAX 8','A330-900','A350-1000','A340-600'].map(a=><option key={a}>{a}</option>)}</select>:x.aircraft_type}</td>
      <td>{x.distance_nm}nm</td><td>{money(x.estimated_revenue)}</td><td>{money(x.estimated_cost)}</td><td className={x.estimated_profit>=0?'good':'bad'}>{money(x.estimated_profit)}</td>
      <td>{editing===x.id?<button onClick={()=>patchAircraft(x)}>Save</button>:<button onClick={()=>{setEditing(x.id);setNewType(x.aircraft_type)}}>Set Aircraft</button>}</td>
    </tr>)}
    </tbody></table></div>
  </>
}
