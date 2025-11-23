// src/pages/Bills.tsx
import { useEffect, useState } from "react";
import api from "../api/client";
import Navbar from "../components/Navbar.tsx";

type Bill = {
  id: number;
  title: string;
  amount: number;
  due_date: string;
  is_paid: boolean;
  repeat_interval?: string | null;
  notes?: string | null;
};

export default function Bills() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [loading, setLoading] = useState(true);

  const [form, setForm] = useState({
    title: "",
    amount: 0,
    due_date: "",
    type: "bill",
    repeat_interval: "monthly",
    reminder_days: "7,3,1",
    notes: ""
  });

  function fetchBills() {
    setLoading(true);
    api.get("/bills").then(r => setBills(r.data)).finally(()=>setLoading(false));
  }

  useEffect(() => {
    fetchBills();
  }, []);

  async function createBill(e: React.FormEvent) {
    e.preventDefault();
    try {
      await api.post("/bills", {
        title: form.title,
        amount: Number(form.amount),
        due_date: form.due_date,
        type: form.type,
        repeat_interval: form.repeat_interval,
        reminder_days: form.reminder_days,
        notes: form.notes
      });
      setForm({ ...form, title: "", amount: 0, due_date: "", notes: "" });
      fetchBills();
    } catch (err) {
      alert("Failed to create bill");
    }
  }

  
  async function markPaid(id:number) {
  try {
    await api.post(`/bills/${id}/mark_paid`);
    fetchBills();
    // notify other parts of app (dashboard) to refresh
    window.dispatchEvent(new Event("bills:updated"));
  } catch (err) {
    alert("Failed to mark paid");
  }
}


  return (
    <div>
      <Navbar />
      <div className="p-6 max-w-4xl mx-auto">
        <h1 className="text-2xl mb-4">Bills</h1>

        <form onSubmit={createBill} className="bg-white p-4 rounded shadow mb-6 grid grid-cols-1 gap-2">
          <div className="flex gap-2">
            <input className="flex-1 p-2 border rounded" placeholder="Title" value={form.title} onChange={e=>setForm({...form, title:e.target.value})} />
            <input type="number" className="w-36 p-2 border rounded" placeholder="Amount" value={form.amount} onChange={e=>setForm({...form, amount: Number(e.target.value)})} />
            <input type="date" className="w-44 p-2 border rounded" value={form.due_date} onChange={e=>setForm({...form, due_date: e.target.value})} />
          </div>
          <div className="flex gap-2">
            <select value={form.repeat_interval ?? ""} onChange={e=>setForm({...form, repeat_interval: e.target.value})} className="p-2 border rounded">
              <option value="monthly">monthly</option>
              <option value="">none</option>
            </select>
            <input className="p-2 border rounded flex-1" placeholder="reminder_days e.g. 7,3,1" value={form.reminder_days} onChange={e=>setForm({...form, reminder_days: e.target.value})} />
            <button className="px-4 py-2 bg-green-600 text-white rounded">Add</button>
          </div>
        </form>

        <div>
          {loading ? <div>Loading bills...</div> : bills.length === 0 ? <div className="text-gray-500">No bills</div> : bills.map(b => (
            <div key={b.id} className="bg-white p-3 rounded shadow mb-2 flex justify-between items-center">
              <div>
                <div className="font-medium">{b.title} {b.is_paid && <span className="text-sm text-green-600 ml-2">(Paid)</span>}</div>
                <div className="text-sm text-gray-500">Due: {b.due_date} • ₹{b.amount}</div>
                <div className="text-sm text-gray-400">{b.repeat_interval ?? ""}</div>
              </div>
              <div className="flex gap-2">
                {!b.is_paid && <button onClick={()=>markPaid(b.id)} className="px-3 py-1 bg-blue-600 text-white rounded">Mark Paid</button>}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}


