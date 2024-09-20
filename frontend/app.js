<script
    src="https://www.datadoghq-browser-agent.com/eu1/v5/datadog-rum.js"
    type="text/javascript">
</script>
<script>
    window.DD_RUM && window.DD_RUM.init({
      clientToken: 'pub9440fba958cca8c9313fa3b7061a338a',
      applicationId: '04a99ea4-d121-4f76-b731-f9514a177be0',
      // `site` refers to the Datadog site parameter of your organization
      // see https://docs.datadoghq.com/getting_started/site/
      site: 'datadoghq.eu',
      service: 'datadog-app',
      env: 'production',
      // Specify a version number to identify the deployed version of your application in Datadog
      // version: '1.0.0',
      sessionSampleRate: 100,
      sessionReplaySampleRate: 100,
      trackUserInteractions: true,
      trackResources: true,
      trackLongTasks: true,
      defaultPrivacyLevel: 'allow',
    });
</script>