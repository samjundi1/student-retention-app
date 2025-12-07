import { useState } from 'react';

function App() {
  const [formData, setFormData] = useState({
    FirstTermGPA: "3.0",
    SecondTermGPA: "3.0",
    HighSchoolAverageMark: "80",
    MathScore: "30",
    FirstLanguage: "1",
    Funding: "2",
    School: "6",
    FastTrack: "2", // 2=No
    Coop: "2",      // 2=No
    Residency: "1",
    Gender: "2",
    PrevEducation: "1",
    AgeGroup: "3",
    EnglishGrade: "9"
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    const payload = {};
    for (const key in formData) {
      payload[key] = parseFloat(formData[key]);
    }

    const apiUrl = window.APP_CONFIG?.API_URL || "http://127.0.0.1:8000";

    try {
      const response = await fetch(`${apiUrl}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server Error (${response.status}): ${errorText}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      setError(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const InputField = ({ label, name, step = "0.1" }) => (
    <div className="flex flex-col text-left">
      <label className="text-sm font-semibold text-gray-700 mb-1">{label}</label>
      <input
        type="number"
        name={name}
        step={step}
        value={formData[name]}
        onChange={handleChange}
        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white text-gray-900" 
        required
      />
    </div>
  );

  const SelectField = ({ label, name, options }) => (
    <div className="flex flex-col text-left">
      <label className="text-sm font-semibold text-gray-700 mb-1">{label}</label>
      <select
        name={name}
        value={formData[name]}
        onChange={handleChange}
        className="p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white text-gray-900"
      >
        {options.map(opt => (
          <option key={opt.value} value={String(opt.value)}>{opt.label}</option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gray-100 font-sans">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-5xl overflow-hidden flex flex-col md:flex-row">
        
        {/* Left Side: Form */}
        <div className="w-full md:w-3/5 p-8 overflow-y-auto max-h-[90vh]">
          <div className="mb-6 text-left">
            <h1 className="text-2xl font-bold text-gray-900">Student Retention AI</h1>
            <p className="text-gray-500 text-sm mt-1">Predict persistence using advanced ML (GPA progression, risk gaps).</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <h3 className="text-gray-800 font-bold border-b border-gray-200 pb-2 mb-4">Academic Performance</h3>
              <div className="grid grid-cols-2 gap-4">
                <InputField label="Term 1 GPA (0-4.5)" name="FirstTermGPA" />
                <InputField label="Term 2 GPA (0-4.5)" name="SecondTermGPA" />
                <InputField label="HS Average (%)" name="HighSchoolAverageMark" step="1" />
                <InputField label="Math Score (0-50)" name="MathScore" step="1" />
              </div>
            </div>

            <div>
              <h3 className="text-gray-800 font-bold border-b border-gray-200 pb-2 mb-4">Program & Background</h3>
              <div className="grid grid-cols-2 gap-4">
                 <SelectField label="English Grade" name="EnglishGrade" options={[
                  { value: 9, label: "Level 170 (High)" },
                  { value: 7, label: "Level 160 (Med)" },
                  { value: 4, label: "Level 141 (Low)" },
                  { value: 2, label: "Level 131 (Very Low)" }
                ]} />
                <SelectField label="School Code" name="School" options={[
                  { value: 6, label: "School 6 (Default)" }
                ]} />
                <SelectField label="FastTrack" name="FastTrack" options={[
                  { value: 1, label: "Yes" }, { value: 2, label: "No" }
                ]} />
                <SelectField label="Co-op" name="Coop" options={[
                  { value: 1, label: "Yes" }, { value: 2, label: "No" }
                ]} />
                <SelectField label="Residency" name="Residency" options={[
                  { value: 1, label: "Domestic" }, { value: 2, label: "International" }
                ]} />
                <SelectField label="Funding" name="Funding" options={[
                  { value: 2, label: "GPOG_FT" }, { value: 4, label: "Intl Regular" }, { value: 1, label: "Apprentice" }, { value: 9, label: "Other" }
                ]} />
              </div>
            </div>

            <div>
              <h3 className="text-gray-800 font-bold border-b border-gray-200 pb-2 mb-4">Demographics</h3>
              <div className="grid grid-cols-2 gap-4">
                <SelectField label="First Language" name="FirstLanguage" options={[
                  { value: 1, label: "English" }, { value: 3, label: "Other" }
                ]} />
                <SelectField label="Age Group" name="AgeGroup" options={[
                  { value: 1, label: "0-18" }, { value: 2, label: "19-20" }, { value: 3, label: "21-25" }, { value: 4, label: "26-30" }, { value: 5, label: "30+" }
                ]} />
                <SelectField label="Gender" name="Gender" options={[
                  { value: 1, label: "Female" }, { value: 2, label: "Male" }, { value: 3, label: "Other" }
                ]} />
                <SelectField label="Prev Education" name="PrevEducation" options={[
                  { value: 1, label: "High School" }, { value: 2, label: "Post Secondary" }
                ]} />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className={`w-full py-3 mt-6 rounded-lg font-bold text-white transition-all transform hover:scale-[1.01] ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 shadow-lg'}`}
            >
              {loading ? "Calculating Risk..." : "Predict Retention"}
            </button>
          </form>
        </div>

        {/* Right Side: Result Display */}
        <div className="w-full md:w-2/5 bg-gray-50 border-l border-gray-200 p-8 flex flex-col justify-center items-center text-center">
          {!result && !error && (
            <div className="text-gray-400">
              <p>Enter student details to see predictions.</p>
            </div>
          )}

          {error && (
            <div className="bg-red-100 text-red-700 p-4 rounded-lg border border-red-200">
              <p className="font-bold">Prediction Failed</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}

          {result && (
            <div className="w-full animate-fade-in">
              <div className={`inline-flex items-center justify-center w-32 h-32 rounded-full mb-6 shadow-inner border-4 ${result.prediction === 1 ? 'bg-green-100 text-green-600 border-green-200' : 'bg-red-100 text-red-600 border-red-200'}`}>
                <span className="text-5xl font-bold">{Math.round(result.probability * 100)}%</span>
              </div>
              
              <h2 className={`text-3xl font-extrabold mb-2 ${result.prediction === 1 ? 'text-green-600' : 'text-red-600'}`}>
                {result.label}
              </h2>
              
              <p className="text-gray-600 mb-6 font-medium">
                {result.prediction === 1 
                  ? "High likelihood of continuing studies." 
                  : "At risk of dropping out."}
              </p>

              <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 text-sm text-gray-500">
                <div className="flex justify-between border-b pb-2 mb-2">
                  <span>Dropout Risk Score:</span>
                  <span className="font-mono font-bold text-gray-700">{(result.risk_score * 100).toFixed(1)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Persistence Prob:</span>
                  <span className="font-mono font-bold text-gray-700">{(result.probability * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;