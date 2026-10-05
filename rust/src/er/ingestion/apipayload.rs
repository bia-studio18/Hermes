//! HTTP API reader.
//!
//! Reuses the existing [`crate::http::HttpClient`] instead of owning a socket:
//! retries, redirects and TLS already live there, and its errors already
//! convert into [`ErError::Ingestion`]. This module only turns a response body
//! into batches.

use crate::data::RecordBatch;
use crate::er::ErError;
use crate::http::{HttpClient, Method};

use super::reader::{Reader, DEFAULT_BATCH_SIZE};
use super::source::{ApiSource, Source};

/// Paging and batching for [`ApiReader`].
#[derive(Debug, Clone)]
pub struct ApiOptions {
    /// Rows per emitted batch.
    pub batch_size: usize,
    /// Query parameter carrying the offset for the next page. `None` means a
    /// single request.
    pub page_param: Option<String>,
    /// Rows requested per API call.
    pub page_size: usize,
}

impl Default for ApiOptions {
    fn default() -> Self {
        Self {
            batch_size: DEFAULT_BATCH_SIZE,
            page_param: None,
            page_size: DEFAULT_BATCH_SIZE,
        }
    }
}

/// Streams an HTTP endpoint into Hermes batches.
///
/// The client is built with default retry and timeout policy; override through
/// [`crate::http::HttpClientBuilder`] when constructing the source.
pub struct ApiReader {
    source: Source,
    options: ApiOptions,
    client: HttpClient,
}

impl ApiReader {
    /// A GET reader over `url`.
    pub fn get(url: impl Into<String>) -> Self {
        Self::request(Method::Get, url)
    }

    /// A reader over `url` using `method`.
    pub fn request(method: Method, url: impl Into<String>) -> Self {
        let api = ApiSource {
            url: url.into(),
            method,
            headers: Vec::new(),
            query: Vec::new(),
            body: None,
            envelope_path: None,
        };
        Self {
            source: Source::Api(api),
            options: ApiOptions::default(),
            client: HttpClient::builder().build(),
        }
    }

    /// Adds request headers.
    pub fn with_headers(mut self, headers: Vec<(String, String)>) -> Self {
        if let Source::Api(api) = &mut self.source {
            api.headers = headers;
        }
        self
    }

    /// Adds query parameters.
    pub fn with_query(mut self, query: Vec<(String, String)>) -> Self {
        if let Source::Api(api) = &mut self.source {
            api.query = query;
        }
        self
    }

    /// Sets the request body and, for anything but GET, leaves the method as-is.
    pub fn with_body(mut self, body: impl Into<String>) -> Self {
        if let Source::Api(api) = &mut self.source {
            api.body = Some(body.into());
        }
        self
    }

    /// Names the object path holding the record array, e.g. `data.items`.
    pub fn with_envelope(mut self, path: Vec<String>) -> Self {
        if let Source::Api(api) = &mut self.source {
            api.envelope_path = Some(path);
        }
        self
    }

    /// Overrides paging and batch size.
    pub fn with_options(mut self, options: ApiOptions) -> Self {
        self.options = options;
        self
    }

    /// The options this reader was built with.
    pub fn options(&self) -> &ApiOptions {
        &self.options
    }

    /// The HTTP client requests go through. Swap it for one with a different
    /// retry or timeout policy before reading.
    pub fn client(&self) -> &HttpClient {
        &self.client
    }
}

impl Reader for ApiReader {
    type Error = ErError;

    fn next_batch(&mut self) -> Result<Option<RecordBatch>, Self::Error> {
        todo!()
    }

    fn source(&self) -> &Source {
        &self.source
    }
}