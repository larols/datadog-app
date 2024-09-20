<script>
  window.DD_RUM && window.DD_RUM.init({
    clientToken: 'pub9440fba958cca8c9313fa3b7061a338a',
    applicationId: '04a99ea4-d121-4f76-b731-f9514a177be0',
    site: 'datadoghq.eu',
    service: 'datadog-app-frontend',  // Update service name if needed
    allowedTracingUrls: [
        "http://backend-service:5000"  // Use the backend service name and port
    ],
    env: 'production',
    version: 'VERSION',  // This will be replaced dynamically
    sessionSampleRate: 100,
    sessionReplaySampleRate: 100,
    trackUserInteractions: true,
    trackResources: true,
    trackLongTasks: true,
    defaultPrivacyLevel: 'allow',
  });

  // Random user data generation for 3 customer segments
  (function() {
    const firstNames = ["John", "Jane", "Sam", "Chris", "Pat", "Alex", "Jamie", "Taylor", "Jordan", "Casey"];
    const lastNames = ["Smith", "Doe", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Moore", "Clark", "Lee"];
    const customerSegments = [
      { idPrefix: 'cust-a-', domain: 'example.com' },
      { idPrefix: 'cust-b-', domain: 'example.io' },
      { idPrefix: 'cust-c-', domain: 'example.net' }
    ];

    function getRandomInt(min, max) {
      return Math.floor(Math.random() * (max - min + 1)) + min;
    }

    function generateUser() {
      const firstName = firstNames[getRandomInt(0, firstNames.length - 1)];
      const lastName = lastNames[getRandomInt(0, lastNames.length - 1)];
      const segment = customerSegments[getRandomInt(0, customerSegments.length - 1)];

      const id = `${segment.idPrefix}${getRandomInt(1000, 9999)}`;
      const email = `${firstName.toLowerCase()}.${lastName.toLowerCase()}@${segment.domain}`;

      return { id, name: `${firstName} ${lastName}`, email };
    }

    const randomUser = generateUser();
    window.DD_RUM?.setUser({
      id: randomUser.id,
      name: randomUser.name,
      email: randomUser.email
    });

    // Send user data to the server when visiting the profile page
    document.addEventListener('DOMContentLoaded', function() {
      if (window.location.pathname === '/profile') {
        fetch('/profile', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(randomUser)
        })
        .then(response => response.text())
        .then(data => document.body.innerHTML = data)
        .catch(error => console.error('Error:', error));
      }
    });
  })();
</script>