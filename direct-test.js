async function runDirectTest() {
  // Replace the text below with your actual sk_... key directly inside the string quotes
  const apiKey = process.env.JEVSTATION_API_KEY; 

  console.log("Connecting to JevStation...");

  try {
    const res = await fetch("https://jevstation.com/api/v1/systemone", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
        "Accept": "application/json"  // Forces the server to respond with data, not a web page
      },
      body: JSON.stringify({
        state: "System Integration Check",
        questions: { 
          is_working: { 
            type: "noul", 
            instructions: "Is Jev responding?" 
          } 
        }
      })
    });

    const textOutput = await res.text();

    try {
      const jsonOutput = JSON.parse(textOutput);
      console.log("✅ SUCCESS! JevStation parsed cleanly:");
      console.log(JSON.stringify(jsonOutput, null, 2));
    } catch (parseError) {
      console.error("❌ Server rejected configuration. Raw printout:");
      console.log(textOutput.substring(0, 300)); 
    }

  } catch (networkError) {
    console.error("❌ Network execution failed:", networkError.message);
  }
}

runDirectTest();