// prettier Dashboard (copy/paste replace)
import { useEffect, useState } from "react";
import api from "../api/client";
import Navbar from "../components/Navbar";

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     api.get("/dashboard")
//       .then(r => setData(r.data))
//       .catch(()=>setData(null))
//       .finally(()=>setLoading(false));
//   }, []);


        // put this inside your component, replacing the existing useEffect
    useEffect(() => {
    // shared fetch function
    const fetchDashboard = async () => {
        setLoading(true);
        try {
        const r = await api.get("/dashboard");
        setData(r.data);
        } catch (e) {
        setData(null);
        console.error("Failed to fetch /dashboard:", e);
        } finally {
        setLoading(false);
        }
    };

    // initial load
    fetchDashboard();

    // live refresh when bills change elsewhere in the app
    const onUpdate = () => {
        fetchDashboard();
    };
    window.addEventListener("bills:updated", onUpdate);

    // cleanup
    return () => window.removeEventListener("bills:updated", onUpdate);
    }, []);


  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-5xl mx-auto p-8">
        <div className="hero">
        <div className="hero-text">
            <h1>SmartDues — Stay on top of your bills</h1>
            <p>Personal bill tracker with reminders, recurring bills and payment history.</p>
            <div className="mt-4">
            <button onClick={() => window.location.href = "/bills"} className="btn btn-brand">Add bill</button>
            <button className="btn btn-ghost ml-3">Import</button>
            </div>
        </div>
        {/* optional right-side small image or stats */}
        </div>



        <section className="bg-white rounded-lg shadow p-6 mb-6">
          <h1 className="text-4xl font-extrabold mb-1 text-slate-800">Dashboard</h1>
          <p className="text-sm text-slate-500">Overview of your unpaid bills and upcoming due dates.</p>
        </section>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white p-6 rounded shadow">
            <div className="text-sm text-gray-500">Total unpaid (this month)</div>
            <div className="text-2xl font-semibold mt-2">₹{loading ? "..." : (data?.total_month_unpaid ?? 0)}</div>
          </div>
          <div className="bg-white p-6 rounded shadow">
            <div className="text-sm text-gray-500">Upcoming (7 days)</div>
            <div className="mt-2">{loading ? "..." : (data?.upcoming_next_7_days?.length ?? 0)} bills</div>
          </div>
          <div className="bg-white p-6 rounded shadow">
            <div className="text-sm text-gray-500">Overdue</div>
            <div className="text-2xl font-bold mt-2">{loading ? "..." : (data?.overdue_count ?? 0)}</div>
          </div>
        </div>

        <section className="mb-6">
          <h2 className="text-xl font-semibold mb-3">Upcoming Bills</h2>
          <div className="space-y-3">
            {loading ? <div>Loading...</div> : (data?.upcoming_next_7_days?.length ? data.upcoming_next_7_days.map((b:any)=>(
              <div key={b.id} className="bg-white p-4 rounded shadow flex justify-between">
                <div>
                  <div className="font-medium">{b.title}</div>
                  <div className="text-sm text-gray-500">Due {b.due_date}</div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-semibold">₹{b.amount}</div>
                  <div className="text-sm text-gray-400">{b.type}</div>
                </div>
              </div>
            )) : <div className="text-gray-500">No upcoming bills</div>)}
          </div>
        </section>
      </main>
    </div>
  );
}


