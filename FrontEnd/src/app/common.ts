export class Codec {
  private encoder: TextEncoder = new TextEncoder();
  private decoder: TextDecoder = new TextDecoder();

  public encode(text: string): Uint8Array {
    return this.encoder.encode(text);
  }

  public decode(arr: Uint8Array): string {
    return this.decoder.decode(arr);
  }
}

export interface LoginResponse {
  name: string;
  tag_id: string;
  token: string;
}
